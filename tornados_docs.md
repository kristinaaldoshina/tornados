The dataset is a combination of 50 files from https://www.ncdc.noaa.gov/stormevents/ftp.jsp, and contains information about tornados in the USA in the 21st century.

__begin_yearmonth:__ 201212 (YYYYMM format)  
The year and month that the event began.

__begin_day:__ 31 (DD format)  
The day of the month that the event began.

__begin_time:__ 2359 (hhmm format)  
The time of day that the event began.

__end_yearmonth:__ 201301 (YYYYMM format)  
The year and month that the event ended.

__end_day:__ 01 (DD format)  
The day of the month that the event ended.

__end_time:__ 0001 (hhmm format)  
The time of day that the event ended.

__episode_id:__ 61280, 62777, 63250  
ID assigned by NWS to denote the storm episode; Episodes may contain multiple Events.
The occurrence of storms and other significant weather phenomena having sufficient intensity
to cause loss of life, injuries, significant property damage, and/or disruption to commerce.

__event_id:__ 383097, 374427, 364175  
ID assigned by NWS for each individual storm event contained within a storm episode.

__state:__ GEORGIA, WYOMING, COLORADO  
The state name where the event occurred (no State ID’s are included here; State Name is
spelled out in ALL CAPS).

__year:__ 2000, 2006, 2012  
The four digit year for the event in this record.

__month_name:__ January, February, March  
The name of the month for the event in this record (spelled out; not abbreviated).

__begin_date_time:__ 2012-01-04 20:48:00 (YYYY-MM_DD hh:mm:ss format)  
24 hour time usually in LST.

__cz_timezone:__ EST-5, MST-7, CST-6  
Time Zone for the County/Parish, Zone or Marine Name. Eastern Standard Time (EST),
Central Standard Time (CST), Mountain Standard Time (MST), etc.

__end_date_time:__ 2012-01-04 20:48:00 (YYYY-MM_DD hh:mm:ss format)  
24 hour time usually in LST.

__injuries_direct:__ 1, 0, 56  
The number of injuries directly caused by the weather event.

__injuries_indirect:__ 0, 15, 87  
The number of injuries indirectly caused by the weather event.

__deaths_direct:__ 0, 45, 23  
The number of deaths directly caused by the weather event.

__deaths_indirect:__ 0, 4, 6  
The number of deaths indirectly caused by the weather event.

__damage_property:__ 0, 10000, 1000000  
The estimated amount of damage to property incurred by the weather event, in dollars.

__damage_crops:__ 0, 10000, 1000000  
The estimated amount of damage to crops incurred by the weather event, in dollars.

__magnitude:__ 0.75, 60, 0.88, 2.75  
The measured extent of the magnitude type ~ only used for wind speeds (in knots) and hail size
(in inches to the hundredth).

__magnitude_type:__ EG, MS, MG, ES  
EG = Wind Estimated Gust; ES = Estimated Sustained Wind; MS = Measured Sustained Wind;
MG = Measured Wind Gust (no magnitude is included for instances of hail).

__tor_f_scale:__ F0, F1, F2, F3, F4, F5, unknown  
Fujita Scale describes the strength of the tornado based on the amount and type of
damage caused by the tornado. The F-scale of damage will vary in the destruction area;
therefore, the highest value of the F-scale is recorded for each event.

- F0 - 40-72 mph - Light damage (e.g., broken branches, shallow-rooted trees pushed over)
- F1 - 73-112 mph - Moderate damage (e.g., mobile homes overturned, moving cars pushed off roads)
- F2 - 113-157 mph - Considerable damage (e.g., roofs torn off, large trees snapped or uprooted)
- F3 - 158-206 mph - Severe damage (e.g., trains overturned, walls torn off houses)
- F4 - 207-260 mph - Devastating damage (e.g., houses leveled, cars thrown significant distances)
- F5 - 261-318 mph - Incredible damage (e.g., strong framed houses swept away, deformation of steel-reinforced structures)

__tor_length:__ 0.66, 1.05, 0.48  
Length of the tornado or tornado segment while on the ground (in kilometers to the tenth).

__tor_width:__ 25, 50, 1760, 10  
Width of the tornado or tornado segment while on the ground (in meters to the tenth).

__begin_range:__ 0.59, 0.69, 4.84, 1.17 (in miles)  
The distance to the nearest tenth of a mile, to the location referenced below.

__begin_azimuth:__ ENE, NW, WSW, S  
16-point compass direction from the location referenced below.

__begin_location:__ PINELAND, CENTER, ORRS, RUSK  
The name of city, town or village from which the range is calculated and the azimuth is
determined.

__end_range:__ see begin_range

__end_azimuth:__ see begin_azimuth

__end_location:__ see begin_location

__begin_lat:__ 29.7898  
The latitude in decimal degrees of the begin point of the event or damage path.

__begin_lon:__ -98.6406  
The longitude in decimal degrees of the begin point of the event or damage path.

__end_lat:__ 29.7158  
The latitude in decimal degrees of the end point of the event or damage path. Signed negative (-)
if in the southern hemisphere.

__end_lon:__ -98.7744  
The longitude in decimal degrees of the end point of the event or damage path. Signed negative
(-) if in the eastern hemisphere.

__episode_narrative:__ A strong upper level system over the southern Rockies lifted northeast
across the plains causing an intense surface low pressure system and attendant warm front to
lift into Nebraska.

The episode narrative depicting the general nature and overall activity of the episode. The
National Weather Service creates the narrative.

__event_narrative:__ Heavy rain caused flash flooding across parts of Wilber. Rainfall of 2 to
3 inches fell across the area.

The event narrative provides descriptive details of the individual event. The National Weather
Service creates the narrative.

__fat_yearmonth:__ 201212 (YYYYMM format)  
The year and month that the fatality happened.

__fat_day:__ 31 (DD format)  
The day of the month that the fatality happened.

__fat_time:__ 2359 (hhmm format)  
The time of day that the fatality happened.

__fatality_id:__ 17582, 17590, 17597, 18222  
ID assigned by NWS to denote the individual fatality that occurred

__fatality_type:__ D , I  
(D = Direct Fatality; I = Indirect Fatality; assignment of this is determined by NWS software;
details below are from NWS Directve 10-1605 at http://www.nws.noaa.gov/directives/sym/pd01016005curr.pdf, Section 2.6) 

__fatality_date:__ 2012-01-04 20:48:00 (YYYY-MM_DD hh:mm:ss format)  
24 hour time usually in LST.

__fatality_age:__ 38, 25, 69, 54  
The age in years of the fatality (sometimes _null_ if unknown)    

__fatality_sex:__ M, F  
The gender of the fatality (sometimes _null_ if unknown)

__fatality_location:__ UT, OU, MH, PS  
Direct Fatality Location:
BF Ball Field
BO Boating
BU Business
CA Camping
CH Church
EQ Heavy Equip/Construction
GF Golfing
IW In Water
LS Long Span Roof
MH Mobile/Trailer Home
OT Other/Unknown
OU Outside/Open Areas
PH Permanent Home
PS Permanent Structure
SC School
TE Telephone
UT Under Tree
VE Vehicle and/or Towed Trailer

__events_yearmonth:__ 201212 (YYYYMM format)  
The year and month that the event happened.

__tor_duration_minutes:__ 20.0, 0.15  
Duration of a tornado (in minutes to the tenth).