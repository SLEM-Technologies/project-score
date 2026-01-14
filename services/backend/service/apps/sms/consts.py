from django.db import models


class SMSEventStatus(models.TextChoices):
    PENDING = 'PENDING'
    IN_PROGRESS = 'IN_PROGRESS'


class SMSHistoryStatus(models.TextChoices):
    PENDING = 'PENDING'
    SENT = 'SENT'
    ERROR = 'ERROR'


SMS_TEMPLATES_CACHE_KEY = 'sms_templates_cache_key'
# Reduced from 700 to 100 to avoid Dialpad API rate limits (fixes 403 errors)
SMS_LIMIT_PER_MINUTE = 200
PHONE_CODE = '+1'
PERIOD_TO_DISPLAY_REMINDERS_IN_YEARS = 3
MIN_EXPIRY_PERIOD_IN_WEEKS = 7
MAX_EXPIRY_PERIOD_IN_YEARS = 3
PATIENTS_CHUNK_SIZE = 200
UPDATE_BATCH_SIZE = 200
CREATE_BATCH_SIZE = 200
SEND_AT_HOUR = 11  # ET
SMS_TIME_ZONE = 'US/Eastern'
DEFAULT_SMS_TEMPLATE_W_LINK = (
    'Hi, this is {scheduler} reaching out on behalf of {practice_name}! {your_pets_capitalized} {be_verb} overdue '
    'for important preventative services. But don\'t worry! You can book an appointment '
    'now for {your_pets}. Let me help you book! {link}'
)
DEFAULT_SMS_TEMPLATE_W_PHONE = (
    'Hi, this is {scheduler} reaching out on behalf of {practice_name}! {your_pets_capitalized} are overdue for '
    'important preventative services. Give us a call at our main phone number {practice_phone_number} so we can discuss the '
    'services due for your pets!'
)
SMS_VARIABLES = (
    'scheduler',
    'practice_name',
    'your_pets_capitalized',
    'your_pets',
    'practice_phone_number',
    'link',
)
OUTCOMES_TO_FILTER_OUT = ('Client declined - pet died', 'Deceased per client')

PHONE_TYPES_TO_EXCLUDE = {
    # 'Home',  removed to send sms for specific practices (e.g. 31438-vss)
    # 'home',  removed to send sms to 86449-vss practice
    # '1+ Number Home',
    # '1+ number - Home',
    # 'HOME',
    # 'HOME-',
    # 'HOme',
    # 'Home #',
    # 'Home (Primary)',
    # 'Home -',
    # 'Home Ph.',
    # 'Home Phone',
    # 'Home Phone Number',
    # 'Home Phone:',
    # 'Home phone',
    # 'Home#',
    # 'Home, a 1+ number',
    # 'Home-',
    # 'Home--',
    # 'HomePhone',
    # 'Phone 1|HOME',
    # 'Phone 1|HOMe',
    # 'Phone 1|HOme',
    # 'Phone 1|Home',
    # 'Phone 1|Home*',
    # 'Phone 1|Home-',
    # 'Phone 1|home',
    # 'Phone 1|home number',
    # 'Phone 1|home phone',
    # 'home phone',
    # 'home#',
    # "home'",
    # 'home #',
    # 'home`',

    '# DISCONNECTED',
    '# Disconnected?',
    '# disconnected',
    '#Disconnected',
    # '247-3370 Home',  # Valid home number - allow SMS
    # '3Home',  # Valid home number - allow SMS
    # '41HOME',  # Valid home number - allow SMS
    # '814HOME',  # Valid home number - allow SMS
    # 'Abby Home',  # Valid home number - allow SMS
    "Adam's work #",
    # 'Aliquippa home',  # Valid home number - allow SMS
    # 'Alissa Home',  # Valid home number - allow SMS
    # 'Amanda home',  # Valid home number - allow SMS
    'Ambree Work',
    'Amie Work',
    # 'Beth Home',  # Valid home number - allow SMS
    "Beth's work phone",
    "Betsy's Work",
    # "Betty's Home #",  # Valid home number - allow SMS
    "Bradley's - Melanie's work",
    # 'Brian Home (son)',  # Valid home number - allow SMS
    'Business',
    'Business 2',
    'Business/Home',
    # 'CHRIS HOME PHONE',  # Valid home number - allow SMS
    'CONFIRM # Home',
    # 'Candice (mom) Home',  # Valid home number - allow SMS
    # 'Carl Home',  # Valid home number - allow SMS
    # "Carol's Home",  # Valid home number - allow SMS
    "Carol's Phone",
    # "Caroline's Home",  # Valid home number - allow SMS
    'Cell-disc',
    'Cellular & Work-FedEx',
    'Cellular - Heidi-DISCONNECTED',
    'Cellular - Susan-not working',
    'Cellular - wrong number',
    'Cellular NON WORKING 2-9-09',
    'Cellular(DISCONNECTED8-7-9)',
    'Cellular- Bob-WRONG #',
    'Cellular- Sarah-DISCONNECTED',
    'Cellular- not in service 3-25',
    'Cellular--WRONG NUMBER6-11-9',
    'Cellular-DISC7-8-10',
    'Cellular-Disconnected',
    'Cellular-Jason-DISCONNECTED',
    'Cellular-Martin-DISCONNECTED',
    'Cellular-Michelle WRONG #',
    'Cellular-disconnected',
    'Cellular-out of service',
    'CellularDISCONNECTED',
    'CellularFAX MACHINE9-7-10-',
    'CellularINCORRECT NO4-5-10',
    'CellularWRONG # 5-21-10',
    # 'Charles Home',  # Valid home number - allow SMS
    # 'Chase home phone',  # Valid home number - allow SMS
    # "Cheryl, Lavern's sister's home",  # Valid home number - allow SMS
    'Cheryl- work',
    'Cheryl-Daughter',
    "Cheryle's Work",
    'Chris - case worker',
    # 'Chris Home',  # Valid home number - allow SMS
    # 'Christine Home',  # Valid home number - allow SMS
    # 'Colorado Home Ph #',  # Valid home number - allow SMS
    'Confirm # Home',
    'Confirm home phone number',
    'Confirm work phone #, add cell',
    'Confirm work phone number',
    'DISCONNECTED',
    'DISCONNECTED7-6-9-',
    # 'Daughter Teri Myers home',  # Valid home number - allow SMS
    # 'Daughter in law home',  # Valid home number - allow SMS
    'David Work',
    'Daytime # (work)',
    # 'Deb Home',  # Valid home number - allow SMS
    "Deb's Work",
    # 'Dee Dochnahl Home',  # Valid home number - allow SMS
    # "Denise's Home #",  # Valid home number - allow SMS
    'Dennis Work',
    # 'Diane Home',  # Valid home number - allow SMS
    'Disconnected',
    "Donna's Work",
    # 'Elaine home',  # Valid home number - allow SMS
    # "Ervin's Knutson's home",  # Valid home number - allow SMS
    # "Estelle's Home",  # Valid home number - allow SMS
    # 'Esther(gma)Home',  # Valid home number - allow SMS
    'FAX',
    'Fax',
    'Fax #',
    'Fax Number',
    'Fax for chargeback',
    # 'Faye Home',  # Valid home number - allow SMS
    # 'Finally Home #',  # Valid home number - allow SMS
    'Foster home - Julie',
    'Francine Work',
    # 'Fred home',  # Valid home number - allow SMS
    'Friend helping',
    'Friend of O',
    "Friend's home",
    "Friend's phone",
    'Friends phone',
    'Front desk',
    # 'Gary Home',  # Valid home number - allow SMS
    "Genise's Work #",
    # 'Gina Home',  # Valid home number - allow SMS
    'H',
    'HER WORK',
    # 'HOME (ST. PETERS)',  # Valid home number - allow SMS
    'HOME - DONT CALL',
    # 'HOME - UNCLE',  # Valid home number - allow SMS
    # 'HOME Dan',  # Valid home number - allow SMS
    # 'HOME PHONE',  # Valid home number - allow SMS
    'HOME UNLISTED',
    # "HOME daughter's",  # Valid home number - allow SMS
    'HOME disconnected',
    # 'HOME- mosaic',  # Valid home number - allow SMS
    'HOME--CALL FIRST',
    'HOME-DISCONNECTE',
    # 'HOME-cl350-9252',  # Valid home number - allow SMS
    'HOME.. disconnected',
    'HOME/WORK',
    'HOME/WORK-SALLY',
    'HONE',
    'HOTEL INDIGO NUMBER',
    'Heidi work',
    'Her Work Phone',
    'Her work',
    'His Work Phone',
    'Home # IS DISCONECTED',
    # 'Home # down 12-6-10',  # Valid home number - allow SMS
    'Home & Fax #',
    'Home & Work',
    'Home & work',
    # 'Home (Benton)',  # Valid home number - allow SMS
    # 'Home (CALL THIS NUMBER)',  # Valid home number - allow SMS
    'Home (Emergency #)',
    # 'Home (Gloria)',  # Valid home number - allow SMS
    'Home (NO TEXT)',
    'Home (Obsolete after 12/04/02)',
    # 'Home (Parents)',  # Valid home number - allow SMS
    'Home (Wrong #) We need new #',
    # 'Home (anthony)',  # Valid home number - allow SMS
    'Home (cell-no text)',
    "Home (disc'd)",
    'Home (disconnected)',
    # "Home (doesn't use cell)",  # Valid home number - allow SMS
    # "Home (doesn't use text/cell)",  # Valid home number - allow SMS
    # 'Home (landline)',  # Valid home number - allow SMS
    'Home (last!)',
    # 'Home (lighting store-OK)',  # Valid home number - allow SMS
    # 'Home (need to dial 262)',  # Valid home number - allow SMS
    # 'Home (no cell #)',  # Valid home number - allow SMS
    'Home (no text)',
    # 'Home (okay to leave a message)',  # Valid home number - allow SMS
    # 'Home (preferred over cell)',  # Valid home number - allow SMS
    'Home (read note)',
    'Home (unlisted)',
    'Home - NOT IN SERVICE',
    'Home - disc',
    'Home - disc 11/8',
    'Home - disc 2/25',
    'Home - disc10/12',
    # 'Home - night shift worker',  # Valid home number - allow SMS
    'Home - not in service',
    # 'Home / Work',  # Valid home number - allow SMS
    # 'Home / Work - Kerry',  # Valid home number - allow SMS
    # 'Home 321-5019',  # Valid home number - allow SMS
    # 'Home Alex',  # Valid home number - allow SMS
    'Home BAD NUMBER',
    # 'Home Barbara',  # Valid home number - allow SMS
    # 'Home Brenda',  # Valid home number - allow SMS
    'Home DISCON 3-3-2009',
    'Home DISCONECTED',
    'Home DISCONNECTED 5-19-2007',
    # 'Home DO NOT SERVICE',  # Valid home number - allow SMS
    # 'Home Don',  # Valid home number - allow SMS
    # 'Home Donna welcom waggin',  # Valid home number - allow SMS
    # 'Home Eric',  # Valid home number - allow SMS
    # 'Home Gary',  # Valid home number - allow SMS
    # 'Home James',  # Valid home number - allow SMS
    # 'Home Juanita',  # Valid home number - allow SMS
    # 'Home Keith',  # Valid home number - allow SMS
    # 'Home Kim',  # Valid home number - allow SMS
    # 'Home Linda',  # Valid home number - allow SMS
    # 'Home Melissa',  # Valid home number - allow SMS
    'Home NOT IN SERVICE',
    # 'Home Not A Working #',  # Valid home number - allow SMS
    # 'Home Office',  # Valid home number - allow SMS
    'Home Phone Number (PRIVATE)',
    # 'Home Phone Spouse',  # Valid home number - allow SMS
    # 'Home Richard',  # Valid home number - allow SMS
    # 'Home Work392-7684',  # Valid home number - allow SMS
    'Home Wrong #',
    'Home and Fax',
    'Home and Fax Call if faxing',
    'Home disc. 1/11',
    # 'Home mothers phone number',  # Valid home number - allow SMS
    'Home phone NOT IN SERVICE',
    # 'Home son is Chris',  # Valid home number - allow SMS
    'Home#- go thru relay service',
    # 'Home(land line)',  # Valid home number - allow SMS
    # 'Home, Work',  # Valid home number - allow SMS
    'Home- CALL FIRST',
    'Home- DISC2/3/12',
    # 'Home- always call this',  # Valid home number - allow SMS
    'Home- disc',
    'Home- disc 6/11',
    'Home- disconnected',
    'Home- until 9-28-14',
    'Home- wrong #',
    'Home-# D.C. 05/12/2009',
    'Home-# out of service',
    # 'Home----Leslie',  # Valid home number - allow SMS
    'Home---DISCONNECTED',
    'Home---DISCONNECTED9-4-07',
    'Home---SEE NOTES',
    # 'Home---not correct',  # Valid home number - allow SMS
    'Home--DISCONECTED',
    'Home--DISCONNECTED12-6-08',
    'Home--DISCONNECTED4-14-09',
    'Home--DISCONNECTED6/07',
    'Home--Disconnected',
    'Home--Disconnected 9-5-07 j',
    'Home--WRONG NUMBER',
    # 'Home--Wm.',  # Valid home number - allow SMS
    # 'Home--this IS a 515 area code',  # Valid home number - allow SMS
    'Home-7-14-08 disconnected',
    'Home-DISCONNECTED',
    'Home-Disconnecte',
    'Home-Disconnected',
    'Home-Moved to California',
    'Home-PH# is D.C.',
    'Home-Ph# D.C.',
    'Home-Ph# D.C. 05/12/09',
    'Home-WRONG #',
    'Home-disc',
    'Home-disc 10/12',
    'Home-disc 2/14',
    'Home-disc 9/9',
    'Home-disc# 12/10',
    'Home-disconncected.',
    'Home-disconnected',
    'Home-fax?',
    # "Home-mom's house",  # Valid home number - allow SMS
    'Home-out of state',
    'Home-wrong #',
    # 'Home/ land line',  # Valid home number - allow SMS
    'Home/(Emergency-Sylvia)',
    'Home/Business',
    'Home/Business #',
    'Home/Emergency',
    'Home/Emergency/Jason Garcia',
    'Home/Fax',
    'Home/Shop#',
    'Home/Work',
    'Home/disc 3/9/12',
    'Home/work',
    # 'Home2',  # Valid home number - allow SMS
    'Home5-1-9-DISCONNECTED',
    'Home7-14-08 Disconnected',
    'Home9-18-08DISCONNECTED',
    # 'Home=leavemessag',  # Valid home number - allow SMS
    'HomeDISCON 1-6-2011',
    'HomeDISCON 9-14-2009',
    'HomeDISCONNECTED7-20-10',
    'HomeDisconnected10-29-09',
    'HomeNEED NEW # 6-11-10',
    # 'HomeNOT RECIVING CALL4-19-10',  # Valid home number - allow SMS
    'HomeWRONG NUMBER1-7-08',
    'HomeWRONG NUMBER8-17-2007',
    'Homedisc',
    'House #',
    'House landline',
    'House line',
    'House phone',
    'Howliday Inn',
    'IDEXX Laboratories',
    'INCORRECT NUMBER',
    'INCORRECT; GET NEW NUMBER',
    'Incorrect telephone #',
    # 'JIM @ AMY HOME',  # Valid home number - allow SMS
    # 'JOETTA HOME',  # Valid home number - allow SMS
    # 'Jack Home',  # Valid home number - allow SMS
    # 'Janice Home',  # Valid home number - allow SMS
    'Jennifer Work',
    "Jessica's work #",
    # 'Joan Vobejda Home',  # Valid home number - allow SMS
    # 'Joanne (home)',  # Valid home number - allow SMS
    # 'John Home',  # Valid home number - allow SMS
    # 'Jolynn Home (daughter)',  # Valid home number - allow SMS
    # 'Joyce Home',  # Valid home number - allow SMS
    # 'Judy home',  # Valid home number - allow SMS
    'Julie/work',
    'KRISTA - Fax',
    # "Kaleb's Home Number",  # Valid home number - allow SMS
    # "Karen's Home",  # Valid home number - allow SMS
    "Karen's Work",
    # "Karen's home",  # Valid home number - allow SMS
    # 'Karen/home',  # Valid home number - allow SMS
    'Katherine work',
    'Kay work',
    # 'Kim Home',  # Valid home number - allow SMS
    # "Kim's Home",  # Valid home number - allow SMS
    "Kim's Work",
    'Kylie Ericson - Fax',
    # 'Laura - Home',  # Valid home number - allow SMS
    'Len Work #',
    # 'Linda Home',  # Valid home number - allow SMS
    # 'Linnae Seaman Home (daughter)',  # Valid home number - allow SMS
    # 'Lisa Home',  # Valid home number - allow SMS
    # 'Local summer home phone',  # Valid home number - allow SMS
    # 'Lona Home',  # Valid home number - allow SMS
    # 'Lori Home',  # Valid home number - allow SMS
    'Lori Work 1 - MMC',
    # "MR'S HOME NUMBER",  # Valid home number - allow SMS
    # 'Mandi Home',  # Valid home number - allow SMS
    'Marcie Work',
    # 'Mary Home',  # Valid home number - allow SMS
    # "Mary Mitchell's Home",  # Valid home number - allow SMS
    'Mary work',
    # 'Maureen home',  # Valid home number - allow SMS
    # 'Michael Home',  # Valid home number - allow SMS
    # "Mike's mother's Home",  # Valid home number - allow SMS
    # 'Miles Home',  # Valid home number - allow SMS
    # 'Missouri Home #',  # Valid home number - allow SMS
    # 'Mom - Home',  # Valid home number - allow SMS
    # "Mom's home",  # Valid home number - allow SMS
    # "Mom's home phone #",  # Valid home number - allow SMS
    # "Mother's Home",  # Valid home number - allow SMS
    # "Mother's home",  # Valid home number - allow SMS
    # 'Mr Home',  # Valid home number - allow SMS
    'Mr. Work',
    # 'Mrs Home',  # Valid home number - allow SMS
    'Mrs Work',
    'Mrs work - try fisrt',
    'NO PHONE',
    'NO SERVICE!!!!!',
    'NOT CURRENT NUMBER',
    'NOT IN SERVICE',
    'NUMBER DISCONECTED',
    # 'Nancy Home',  # Valid home number - allow SMS
    'Need new Phone# - disconnected',
    'No longer in service',
    'No longer valid',
    'No phone number',
    'Noah Work',
    'Not Her Number/leave message',
    'Not Owner Number',
    "Not his phone number DON'T USE",
    'Not in service',
    'Not right number',
    'Number Declined for Safety',
    'Number Disconnect',
    'Number Disconnected',
    'Number not in service',
    'O',
    'Office',
    'Pager',
    # "Parent's Home",  # Valid home number - allow SMS
    # "Parent's Home Ph",  # Valid home number - allow SMS
    # "Parent's home #",  # Valid home number - allow SMS
    "Parent's house",
    # 'Parents Home in Longmont',  # Valid home number - allow SMS
    'Pat work',
    "Pat's Work",
    'Patricia Work',
    # 'Patty Home',  # Valid home number - allow SMS
    'Pattys Work',
    'Pay Fax',
    'Pay Phone',
    # 'Pgh, home',  # Valid home number - allow SMS
    'Phone # D.C.',
    'Phone 1|# is disconn.',
    'Phone 1|12/28/21 disconn',
    # 'Phone 1|2154317249HOME',  # Valid home number - allow SMS
    # 'Phone 1|367-2435 home',  # Valid home number - allow SMS
    # 'Phone 1|394-4470HOME',  # Valid home number - allow SMS
    # 'Phone 1|5HOME',  # Valid home number - allow SMS
    # 'Phone 1|ASHES Home',  # Valid home number - allow SMS
    # "Phone 1|April's Home",  # Valid home number - allow SMS
    # 'Phone 1|Canada home phon',  # Valid home number - allow SMS
    'Phone 1|HOME # disc',
    # 'Phone 1|HOME 246-3501',  # Valid home number - allow SMS
    # 'Phone 1|HOME 303-3202',  # Valid home number - allow SMS
    # 'Phone 1|HOME 329-4326',  # Valid home number - allow SMS
    # 'Phone 1|HOME 338-7743',  # Valid home number - allow SMS
    # 'Phone 1|HOME 347-0815',  # Valid home number - allow SMS
    # 'Phone 1|HOME 366-7767',  # Valid home number - allow SMS
    # 'Phone 1|HOME 368-3415',  # Valid home number - allow SMS
    # 'Phone 1|HOME 533-7127',  # Valid home number - allow SMS
    # 'Phone 1|HOME 817-875-64',  # Valid home number - allow SMS
    # 'Phone 1|HOME 913-5624',  # Valid home number - allow SMS
    # 'Phone 1|HOME 914-843-82',  # Valid home number - allow SMS
    # 'Phone 1|HOME 952-8101',  # Valid home number - allow SMS
    # 'Phone 1|HOME280-7035',  # Valid home number - allow SMS
    # 'Phone 1|HOME281-6271',  # Valid home number - allow SMS
    # 'Phone 1|HOME319-3630',  # Valid home number - allow SMS
    # 'Phone 1|HOME347-4585',  # Valid home number - allow SMS
    # 'Phone 1|HOME368-2170',  # Valid home number - allow SMS
    # 'Phone 1|HOME393-2670',  # Valid home number - allow SMS
    # 'Phone 1|HOME400-4853',  # Valid home number - allow SMS
    # 'Phone 1|HOME728-6763',  # Valid home number - allow SMS
    # 'Phone 1|HOMEsister',  # Valid home number - allow SMS
    'Phone 1|Home #disc',
    # 'Phone 1|Home 304-6503',  # Valid home number - allow SMS
    'Phone 1|Home discntd#',
    # 'Phone 1|Home-use first',  # Valid home number - allow SMS
    'Phone 1|Home/Training #',
    # 'Phone 1|Home798-2780',  # Valid home number - allow SMS
    # 'Phone 1|Home?',  # Valid home number - allow SMS
    # "Phone 1|Kathy's Home #",  # Valid home number - allow SMS
    # 'Phone 1|Laura - Home',  # Valid home number - allow SMS
    # "Phone 1|MOM'S HOME",  # Valid home number - allow SMS
    'Phone 1|OWNER NEVER HOME',
    'Phone 1|Shop (Work)',
    # "Phone 1|Stefanie's Home",  # Valid home number - allow SMS
    'Phone 1|WORK',
    'Phone 1|Work',
    # 'Phone 1|cell /HOME453-55',  # Valid home number - allow SMS
    'Phone 1|cell disconnecte',
    'Phone 1|fax machine',
    # 'Phone 1|home (husband)',  # Valid home number - allow SMS
    # 'Phone 1|home - call firs',  # Valid home number - allow SMS
    # 'Phone 1|home call 4 ash',  # Valid home number - allow SMS
    # 'Phone 1|home, call for r',  # Valid home number - allow SMS
    'Phone 1|wk her desk',
    'Phone 1|work',
    'Phone 1|wrk',
    # 'Phone 1|wrkHome',  # Valid home number - allow SMS
    'Phone 1|wwork',
    'Phone1-out of service',
    'Private Home #',
    # "Randy's home #",  # Valid home number - allow SMS
    "Rene's Work",
    "Renee's Work",
    "Rhonda's Work",
    # 'Richard Home',  # Valid home number - allow SMS
    'Rick work',
    # 'Rita Home',  # Valid home number - allow SMS
    "Robert's Work",
    # 'Robin Home',  # Valid home number - allow SMS
    'Robin Work',
    "Roger's Work",
    # 'Ronald Home',  # Valid home number - allow SMS
    # 'Ronnie Home #1',  # Valid home number - allow SMS
    # 'Rose Home',  # Valid home number - allow SMS
    # 'Ryan Home',  # Valid home number - allow SMS
    # "Sam's Home phone",  # Valid home number - allow SMS
    # 'Sandy home (daughter)',  # Valid home number - allow SMS
    'Secondary Home',
    'Secondary home :',
    'Secondary(Foster)',
    'Secondary(work)',
    "Secondary/ O's mother",
    # "Sheryl's Home",  # Valid home number - allow SMS
    # 'Sp. Home',  # Valid home number - allow SMS
    'Sp. Work',
    'Spouse Work Phone',
    "Spouse's Work",
    "Spouse's Work Levi",
    "Spouse's Work-Nathan",
    'Spouse/Co-owner Work Phone',
    # "Steve's Home",  # Valid home number - allow SMS
    'Sue - work',
    # "Sue's Home",  # Valid home number - allow SMS
    # 'Summer home #',  # Valid home number - allow SMS
    # 'Susan Home',  # Valid home number - allow SMS
    # 'Sylvia Home',  # Valid home number - allow SMS
    # 'Ted Heitman Home #',  # Valid home number - allow SMS
    'Through Sorenson Rely Service',
    # 'Tiggerr home',  # Valid home number - allow SMS
    "Tim's Cell/Disconnected",
    # 'Toni Home',  # Valid home number - allow SMS
    'UPDATE - WRONG NUMBER',
    # "Victor's Home",  # Valid home number - allow SMS
    'Video Relay Service',
    # 'Viginia- Home',  # Valid home number - allow SMS
    'W',
    # 'WI Home',  # Valid home number - allow SMS
    'WORK',
    'WORK (SASS)',
    'WORK 342-4451',
    'WORK 377-7114',
    # 'WORK SMITH FUNERAL HOME',  # Valid home number - allow SMS
    'WORK-BCSC',
    'WORK-MINDY',
    'WRONG #',
    'WRONG NUMBER',
    'WRONG NUMBER?',
    'WRONG PHONE NUMBER',
    # "Walt's Home",  # Valid home number - allow SMS
    'Wife Work',
    # 'Wisconsin Home',  # Valid home number - allow SMS
    # 'Wisconsin Home #',  # Valid home number - allow SMS
    'Work',
    'Work #',
    'Work # (where cat lives)',
    'Work #/Fax #',
    'Work (Bonnie)',
    'Work (Gary Yoemans)',
    'Work (Nancy)',
    'Work (dad)',
    'Work - Aaron',
    'Work - Adam',
    'Work - Angie',
    'Work - Ask Reception for Dr. Kaiser',
    'Work - Beans Auto Jamie',
    'Work - Christine',
    'Work - DP Plumbing',
    "Work - Farmer's Savings",
    'Work - Fred',
    'Work - Jeromy',
    'Work - Joan',
    'Work - Joyce',
    'Work - Lauri',
    'Work - Lenny',
    'Work - Office',
    'Work - Platteville Vet',
    'Work - Shawn',
    'Work - Tonia',
    'Work - Vanessa',
    'Work - Woodcock Twp',
    'Work - primary!',
    'Work 1',
    'Work 2',
    'Work 229 2181',
    'Work 2293559',
    'Work 246 4341',
    'Work Phone',
    'Work Phone1:',
    'Work Phone2:',
    'Work Phone:',
    'Work Sam',
    'Work Until Noon M-F',
    'Work X21953',
    'Work X3000',
    # 'Work and Home',  # Valid home number - allow SMS
    'Work daytime',
    'Work during the day 8-4:30',
    'Work jeff',
    'Work number',
    'Work phone',
    # 'Work+Home',  # Valid home number - allow SMS
    'Work, ext 111',
    'Work- Mineral Point School',
    'Work- PBF INC',
    'Work- Sally',
    'Work- U Haul',
    'Work- kris',
    'Work-Ashley',
    'Work-Bank number',
    'Work-Brian',
    'Work-Cheryl',
    'Work-Dale',
    'Work-Elizabeth',
    'Work-Ernie',
    'Work-Hardees',
    'Work-Jamie',
    'Work-Jason',
    'Work-Kevin',
    'Work-Kurt(son)',
    'Work-Laurie',
    'Work-Marie',
    'Work-Mr',
    'Work-Mrs',
    'Work-Ms. ext.55875',
    'Work-Rena',
    'Work-Rita',
    'Work-Ryan',
    'Work-Stacia',
    'Work-Stella(mom)',
    'Work-TransWorld',
    'Work-Trent',
    'Work-shop number',
    'Work-week day number to call',
    'Work/ Brittanie',
    'Work/Home',
    'Work2',
    'Working number',
    'Wrong Number',
    'Wrong Number-NOT KRISTINA',
    'Wrong number',
    'Zach Work',
    'call this # with bloodwork results :',
    'cell - disc',
    'cell-disc 9/16',
    'confirm # Home',
    'disconnected',
    'fax',
    'h',
    # 'hOME',  # Valid home number - allow SMS
    'his work',
    'his worker - Aaron',
    'home & work',
    # 'home (Alaska)',  # Valid home number - allow SMS
    # 'home (mothers # ) Junne',  # Valid home number - allow SMS
    'home (unlisted)',
    'home - disconnected',
    # 'home / work',  # Valid home number - allow SMS
    'home--disconnected l/19/98',
    'home--unlisted',
    'home--unpublished',
    'home-unlisted',
    # 'home-unpb.',  # Valid home number - allow SMS
    'home/fax',
    'home/office',
    'home/work',
    "home/work'",
    # 'homehome]',  # Valid home number - allow SMS
    # 'homel',  # Valid home number - allow SMS
    'homne',
    'homr',
    'hosp phone',
    'house phone',
    'husband work',
    # "mom's Home",  # Valid home number - allow SMS
    # "mother in law's home",  # Valid home number - allow SMS
    'mr work',
    # 'new home number',  # Valid home number - allow SMS
    'no Phone',
    # 'no home phone',  # Valid home number - allow SMS
    'no telephone',
    'non-published number 12/24/97',
    'non-working ph#',
    'none listed for PR rab clinic',
    'not in service 9/30/10',
    # "parents' home",  # Valid home number - allow SMS
    'primary (work phone)',
    'unlisted - home',
    # 've.HOME',  # Valid home number - allow SMS
    'wife work',
    'wk brian',
    'work',
    'work #',
    'work # call between 12-12:30PM',
    'work - The Print shop',
    'work 279--3340',
    'work Barger Leasing',
    'work Ext 436',
    'work call first',
    'work phone',
    'work#',
    'work, call this FIRST',
    'work- 8-5pm',
    'work/Kal',
    'work/home',
    'wrong #',
    'wrong # & address',
    "wrong #? don't text",
    'wrong number',
}
