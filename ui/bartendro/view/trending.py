# -*- coding: utf-8 -*-
import time
from bartendro import app, db
from sqlalchemy import desc, func
from flask import Flask, request, render_template
from flask.ext.login import login_required, current_user
from bartendro.model.drink import Drink
from bartendro.model.drink_log import DrinkLog
from bartendro.model.drink_log_booze import DrinkLogBooze
from bartendro.model.booze import Booze
from bartendro.model.booze_group import BoozeGroup
from bartendro.model.user import User
from bartendro.form.booze import BoozeForm
from bartendro.view.drink.drink import is_ip_allowed_to_pour_drinks

DEFAULT_TIME = 12
display_info = {
    12 : 'Drinks poured in the last 12 hours.',
    72 : 'Drinks poured in the last 3 days.',
    168 : 'Drinks poured in the last week.',
    0 : 'All drinks ever poured'
}

@app.route('/trending')
def trending_drinks():
    return trending_drinks_detail(DEFAULT_TIME)

@app.route('/trending/<int:hours>')
def trending_drinks_detail(hours):

    title = "Trending drinks"
    log = db.session.query(DrinkLog).order_by(desc(DrinkLog.time)).first() or 0
    if log:
        if not log.time:
            enddate = int(time.time())
        else:
            enddate = log.time
    
        try:
            txt = display_info[hours]
        except IndexError:
            txt = "Drinks poured in the last %d hours" % hours

        # if a number of hours is 0, then show for "all time"
        if hours:
            begindate = enddate - (hours * 60 * 60)
        else:
            begindate = 0
    else:
	begindate = 0
        enddate = 0
        txt = ""

    total_number = db.session.query("number")\
                 .from_statement("""SELECT count(*) as number
                                      FROM drink_log 
                                     WHERE drink_log.time >= :begin 
                                       AND drink_log.time <= :end""")\
                 .params(begin=begindate, end=enddate).first()

    total_volume = db.session.query("volume")\
                 .from_statement("""SELECT sum(drink_log.size) as volume 
                                      FROM drink_log 
                                     WHERE drink_log.time >= :begin 
                                       AND drink_log.time <= :end""")\
                 .params(begin=begindate, end=enddate).first()

    total_volume_of_pure_alcohol = calculate_total_volume_of_pure_alcohol(begindate, enddate)
    
    beer_equivalent = "{0:.2f}".format(calculate_beer_equivalent(total_volume_of_pure_alcohol))
                
    bac = "{0:.2f}".format(calculate_bac(total_volume_of_pure_alcohol))
            
    try:
        user_id_sql_string = """AND drink_log.user_id = """ + str(current_user.id)
    except AttributeError:
        #no user is logged in, show overview
        user_id_sql_string = ""
    top_drinks = db.session.query("id", "name", "number", "volume")\
                 .from_statement("""SELECT drink.id, 
                                           drink_name.name,
                                           count(drink_log.drink_id) AS number, 
                                           sum(drink_log.size) AS volume 
                                      FROM drink_log, drink_name, drink 
                                     WHERE drink_log.drink_id = drink_name.id 
                                       AND drink_name.id = drink.id
                                       """ + str(user_id_sql_string) + """
                                       AND drink_log.time >= :begin AND drink_log.time <= :end 
                                  GROUP BY drink_name.name 
                                  ORDER BY count(drink_log.drink_id) desc;""")\
                 .params(begin=begindate, end=enddate).all()




    return render_template("trending", top_drinks = top_drinks, options=app.options,
                                       title="Trending drinks",
                                       txt=txt,
                                       total_number=total_number[0],
                                       total_volume=total_volume[0],
                                       total_volume_of_pure_alcohol=total_volume_of_pure_alcohol,
                                       beer_equivalent=beer_equivalent,
                                       bac=bac,
                                       hours=hours,
                                       allowed_to_pour=is_ip_allowed_to_pour_drinks(request.remote_addr))
                                       
                                       
def calculate_total_volume_of_pure_alcohol(begindate, enddate):
    # calculate the total amount of pure alcohol drunk during the selected period
    
    try:
        drink_log_booze_of_current_user_with_alcohol = db.session.query(DrinkLog, DrinkLogBooze, Booze)\
            .filter(DrinkLog.id==DrinkLogBooze.drink_log_id)\
            .filter(DrinkLog.user_id==current_user.id)\
            .filter(DrinkLogBooze.booze_id==Booze.id)\
            .filter(Booze.type==1)\
            .filter(DrinkLog.time>=begindate)\
            .filter(DrinkLog.time<=enddate).all()
    except AttributeError as e:
        # no user is logged in, take all drinks in drink log
        drink_log_booze_of_current_user_with_alcohol = db.session.query(DrinkLog, DrinkLogBooze, Booze)\
            .filter(DrinkLog.id==DrinkLogBooze.drink_log_id)\
            .filter(DrinkLogBooze.booze_id==Booze.id)\
            .filter(Booze.type==1)\
            .filter(DrinkLog.time>=begindate)\
            .filter(DrinkLog.time<=enddate).all()
    
    total_volume_of_pure_alcohol = 0.0
    for drink_log_booze in drink_log_booze_of_current_user_with_alcohol:
        amount = drink_log_booze.DrinkLogBooze.amount
        abv = drink_log_booze.Booze.abv
        total_volume_of_pure_alcohol += float(amount) * (float(abv)/100)
    return total_volume_of_pure_alcohol
    
def calculate_bac(pure_alcohol):
    """ calculate bac in 1/1000
    
    Calc GKW (Total amount of water in body in l) see. Watson-Formula Wikipedia
    http://de.wikipedia.org/wiki/Blutalkoholkonzentration#Berechnung_der_BAK
    
    TODO: use better model see http://www.forensicscience.pl/pfs/50_gubala.pdf
    """
    
    gkw = 0
    
    try:
        user = db.session.query(User).filter(User.id==current_user.id).one()
    except AttributeError as e:
        "No user logged in, bac can't be calculated."
        return 0
    
    if user.sex == "male":
        gkw = 2.447 - 0.09516*float(user.age)+0.1074*float(user.height)+0.3362*float(user.weight)
    else:
        gkw = 0.203 - 0.07*float(user.age)+0.1069*float(user.height)+0.2466*float(user.weight)

    # Calc distribution factor
    
    BLOOD_DENSITY = 1.005
    FRACTION_OF_WATER_IN_BLOOD = 0.8
    ALCOHOL_DENSITY = 0.8

    distribution_factor = (BLOOD_DENSITY * gkw) / (FRACTION_OF_WATER_IN_BLOOD * float(user.weight))
    mass_of_alcohol = pure_alcohol * ALCOHOL_DENSITY	

    #Widmark-Formula for theoretical maximum BAC in 1/1000
    bac = mass_of_alcohol / (float(user.weight) * distribution_factor)

    return bac
    
def calculate_beer_equivalent(pure_alcohol):
    
    BEER_BOTTLE_SIZE_IN_ML = 330.0
    BEER_ABV_IN_PERCENT = 5.1
    alcohol_in_beer_in_ml = float(BEER_BOTTLE_SIZE_IN_ML)*(BEER_ABV_IN_PERCENT/100)
    
    return pure_alcohol/alcohol_in_beer_in_ml

