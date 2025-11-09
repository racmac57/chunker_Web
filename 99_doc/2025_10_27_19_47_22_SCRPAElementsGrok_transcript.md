# Scrpaelementsgrok

**Processing Date:** 2025-10-27 19:47:22
**Source File:** SCRPAElementsGrok.docx
**Total Chunks:** 3

---

Below is a comprehensive outline of the specified crimes from the 2019 National Incident-Based Reporting System (NIBRS) User Manual, focusing on Burglary to Commercial Buildings, Burglary to Residential Structures, Burglary of a Motor Vehicle, Theft of Motor Vehicle, Robbery, and all Sexual Offenses. Each crime includes its NIBRS offense code, definition, and the mandatory, conditional, and optional data elements and sub-elements (data values) required for entry into the NIBRS database. The sub-elements are presented in numbered lists to facilitate the creation of dropdown menus for standardized data entry, as requested. The outline adheres to the formal tone and structured format specified, ensuring clarity and precision. Note that "Burglary of a Motor Vehicle" is interpreted as "Theft From Motor Vehicle" (23F), as NIBRS does not classify motor vehicle break-ins as burglary but as a larceny/theft offense, unless specified otherwise. Outline of Specified NIBRS Crimes, Elements, and Sub-Elements
I. Crimes Against Property
These offenses aim to obtain money, property, or some other benefit and are counted as one offense per distinct operation, except for Motor Vehicle Theft, which is one offense per stolen vehicle. A. Burglary/Breaking and Entering
Burglary to Commercial Buildings (220)
Definition: The unlawful entry into a commercial building or other structure (e.g., office, store, warehouse) with the intent to commit a felony or a theft. Data Elements and Sub-Elements:
Data Element 1 (ORI) (mandatory):
9-character ORI code
Data Element 2 (Incident Number) (mandatory):
Up to 12-character incident number
Data Element 2A (Cargo Theft) (mandatory):
Y = Yes
N = No
Data Element 3 (Incident Date) (mandatory):
YYYYMMDD (Year, Month, Day)
Data Element 4 (Cleared Exceptionally) (mandatory if cleared):
A = Death of Offender
B = Prosecution Declined
C = In Custody of Other Jurisdiction
D = Victim Refused to Cooperate
E = Juvenile/No Custody
N = Not Applicable
Data Element 5 (Exceptional Clearance Date) (conditional, if cleared exceptionally):
YYYYMMDD
Data Element 6 (UCR Offense Code) (mandatory):
220 = Burglary/Breaking and Entering
Data Element 7 (Offense Attempted/Completed) (mandatory):
A = Attempted
C = Completed
Data Element 8 (Offender Suspected of Using) (mandatory):
A = Alcohol
C = Computer Equipment (Handheld Devices)
D = Drugs/Narcotics
N = Not Applicable
Data Element 8A (Bias Motivation) (mandatory):
11 = Anti-White
12 = Anti-Black or African American
13 = Anti-American Indian or Alaska Native
14 = Anti-Asian
15 = Anti-Native Hawaiian or Other Pacific Islander
16 = Anti-Multiple Races, Group
21 = Anti-Arab
22 = Anti-Hispanic or Latino
23 = Anti-Other Race/Ethnicity/Ancestry
31 = Anti-Jewish
32 = Anti-Catholic
33 = Anti-Protestant
34 = Anti-Islamic (Muslim)
35 = Anti-Other Religion
36 = Anti-Multi-Religious Group
37 = Anti-Atheist/Agnostic
38 = Anti-Mormon
39 = Anti-Jehovah’s Witness
41 = Anti-Eastern Orthodox
42 = Anti-Other Christian
43 = Anti-Buddhist
44 = Anti-Hindu
45 = Anti-Sikh
51 = Anti-Gay (Male)
52 = Anti-Lesbian
53 = Anti-Lesbian, Gay, Bisexual, or Transgender (Mixed Group)
54 = Anti-Transgender
55 = Anti-Gender Non-Conforming
61 = Anti-Physical Disability
62 = Anti-Mental Disability
71 = Anti-Male
72 = Anti-Female
88 = None (No Bias)
99 = Unknown (Bias Unknown)
Data Element 9 (Location Type) (mandatory):
01 = Air/Bus/Train Terminal
02 = Bank/Savings and Loan
03 = Bar/Nightclub
04 = Church/Synagogue/Temple/Mosque
05 = Commercial/Office Building
06 = Construction Site
07 = Convenience Store
08 = Department/Discount Store
09 = Drug Store/Doctor’s Office/Hospital
10 = Field/Woods
11 = Government/Public Building
12 = Grocery/Supermarket
13 = Highway/Road/Alley/Street/Sidewalk
14 = Hotel/Motel/Etc. 15 = Jail/Prison/Penitentiary/Corrections Facility
16 = Lake/Waterway/Beach
17 = Liquor Store
18 = Parking Lot/Garage/Drop Lot
19 = Rental Storage Facility
20 = Residence/Home
21 = Restaurant
22 = School/College
23 = Service/Gas Station
24 = Specialty Store
25 = Other/Unknown
37 = Abandoned/Condemned Structure
38 = Amusement Park
39 = Arena/Stadium/Fairgrounds/Coliseum
40 = ATM Separate from Bank
41 = Auto Dealership New/Used
42 = Camp/Campground
44 = Daycare Facility
45 = Dock/Wharf/Freight/Modal Terminal
46 = Farm Facility
47 = Gambling Facility/Casino/Race Track
48 = Industrial Site
49 = Military Installation
50 = Park/Playground
51 = Rest Area
52 = School-College/University
53 = School-Elementary/Secondary
54 = Shelter-Mission/Homeless
55 = Shopping Mall
56 = Tribal Lands
57 = Community Center
58 = Cyberspace
Data Element 10 (Number of Premises Entered) (mandatory):
01-99
Data Element 11 (Method of Entry) (mandatory):
F = Forced Entry
N = No Forced Entry
Data Element 12 (Type Criminal Activity/Gang Information) (mandatory, up to three):
B = Buying/Receiving
C = Cultivating/Manufacturing/Publishing
D = Distributing/Selling
E = Exploiting Children
J = Juvenile Gang
O = Operating/Promoting/Assisting
P = Possessing/Concealing
T = Transporting/Transmitting/Importing
U = Using/Consuming
G = Other Gang
N = None/Unknown
Data Element 14 (Type Property Loss/Etc.) (mandatory):
1 = None
2 = Burned
3 = Counterfeited/Forged
4 = Damaged/Destroyed
5 = Recovered
6 = Seized
7 = Stolen/Etc. 8 = Unknown
Data Element 15 (Property Description) (mandatory):
01 = Aircraft
02 = Alcohol
03 = Automobile
04 = Bicycle
05 = Bus
06 = Clothes/Furs
07 = Computer Hardware/Software
08 = Consumable Goods
09 = Credit/Debit Cards
10 = Drugs/Narcotics
11 = Drug/Narcotic Equipment
12 = Farm Equipment
13 = Firearms
14 = Gambling Equipment
15 = Heavy Construction/Industrial Equipment
16 = Household Goods
17 = Jewelry/Precious Metals/Gems
18 = Livestock
19 = Merchandise
20 = Money
21 = Negotiable Instruments
22 = Non-Negotiable Instruments
23 = Office-Type Equipment
24 = Other Motor Vehicles
25 = Purses/Handbags/Wallets
26 = Radios/TVs/VCRs/DVD Players
27 = Recordings-Audio/Video
28 = Recreational Vehicles
29 = Structures-Single Occupancy Dwellings
30 = Structures-Other Dwellings
31 = Structures-Other Commercial/Business
32 = Structures-Industrial/Manufacturing
33 = Structures-Public/Community
34 = Structures-Storage
35 = Structures-Other
36 = Tools
37 = Trucks
38 = Vehicle Parts/Accessories
39 = Watercraft
41 = Aircraft Parts/Accessories
42 = Artistic Supplies/Accessories
43 = Building Materials
44 = Camping/Hunting/Fishing Equipment/Supplies
45 = Chemicals
46 = Collections/Collectibles
47 = Crops
48 = Documents/Personal or Business
49 = Explosives
59 = Firearm Accessories
60 = Fuel
61 = Identity Documents
62 = Identity-Intangible
64 = Law Enforcement Equipment
65 = Lawn/Yard/Garden Equipment
66 = Logging Equipment
67 = Medical/Medical Lab Equipment
68 = Metals, Non-Precious
69 = Musical Instruments
70 = Pets
71 = Photographic/Optical Equipment
72 = Portable Electronic Communications
73 = Recreational/Sports Equipment
74 = Scrap Metal
75 = Tobacco
76 = Trailers
77 = Watercraft Equipment/Parts/Accessories
78 = Weapons-Other
88 = Pending Inventory (Unknown)
99 = Other
Data Element 16 (Value of Property) (mandatory):
Numeric value in whole dollars
Data Element 17 (Date Recovered) (conditional, if property recovered):
YYYYMMDD
Data Element 36 (Offender Sequence Number) (mandatory):
00 = Unknown
01-99 = Offender Sequence Number
Data Element 37 (Age of Offender) (mandatory):
00 = Unknown
01-98 = Years Old
99 = Over 98 Years Old
Data Element 38 (Sex of Offender) (mandatory):
M = Male
F = Female
U = Unknown
Data Element 39 (Race of Offender) (mandatory):
W = White
B = Black or African American
I = American Indian or Alaska Native
A = Asian
P = Native Hawaiian or Other Pacific Islander
U = Unknown
Data Element 39A (Ethnicity of Offender) (optional):
H = Hispanic or Latino
N = Not Hispanic or Latino
U = Unknown
Burglary to Residential Structures (220)
Definition: The unlawful entry into a residential structure (e.g., house, apartment, condominium) with the intent to commit a felony or a theft. Data Elements and Sub-Elements:
Identical to Burglary to Commercial Buildings (220), except the Data Element 9 (Location Type) will typically be:
20 = Residence/Home
29 = Structures-Single Occupancy Dwellings (in Data Element 15, if applicable)
30 = Structures-Other Dwellings (in Data Element 15, if applicable)
B. Larceny/Theft Offenses
Theft From Motor Vehicle (23F)
Definition: The unlawful taking of property from within a motor vehicle, not constituting burglary. Data Elements and Sub-Elements:
Same as Burglary to Commercial Buildings (220), except:
Data Element 6 (UCR Offense Code) (mandatory):
23F = Theft From Motor Vehicle
Data Element 10 (Number of Premises Entered): Not applicable
Data Element 11 (Method of Entry): Not applicable
C. Motor Vehicle Theft
Motor Vehicle Theft (240)
Definition: The theft or attempted theft of a motor vehicle. Data Elements and Sub-Elements:
Same as Burglary to Commercial Buildings (220), except:
Data Element 6 (UCR Offense Code) (mandatory):
240 = Motor Vehicle Theft
Data Element 10 (Number of Premises Entered): Not applicable
Data Element 11 (Method of Entry): Not applicable
Data Element 18 (Number of Stolen Motor Vehicles) (mandatory):
00-99
Data Element 19 (Number of Recovered Motor Vehicles) (conditional, if recovered):
00-99
D. Robbery
Robbery (120)
Definition: The taking or attempting to take anything of value from the care, custody, or control of a person or persons by force or threat of force or violence and/or by putting the victim in fear. Data Elements and Sub-Elements:
Data Element 1 (ORI) (mandatory):
9-character ORI code
Data Element 2 (Incident Number) (mandatory):
Up to 12-character incident number
Data Element 2A (Cargo Theft) (mandatory):
Y = Yes
N = No
Data Element 3 (Incident Date) (mandatory):
YYYYMMDD
Data Element 4 (Cleared Exceptionally) (mandatory if cleared):
Same as Burglary to Commercial Buildings (220)
Data Element 5 (Exceptional Clearance Date) (conditional, if cleared exceptionally):
YYYYMMDD
Data Element 6 (UCR Offense Code) (mandatory):
120 = Robbery
Data Element 7 (Offense Attempted/Completed) (mandatory):
A = Attempted
C = Completed
Data Element 8 (Offender Suspected of Using) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 8A (Bias Motivation) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 9 (Location Type) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 12 (Type Criminal Activity/Gang Information) (mandatory, up to three):
Same as Burglary to Commercial Buildings (220)
Data Element 13 (Type Weapon/Force Involved) (mandatory):
11 = Firearm (Unspecified)
12 = Handgun
13 = Rifle
14 = Shotgun
15 = Other Firearm
20 = Knife/Cutting Instrument
30 = Blunt Object
35 = Motor Vehicle/Vessel
40 = Personal Weapons (Hands, Feet, Teeth, Etc.) 50 = Poison
60 = Explosives
65 = Fire/Incendiary Device
70 = Drugs/Narcotics/Sleeping Pills
85 = Asphyxiation
90 = Other
95 = Unknown
99 = None
Data Element 14 (Type Property Loss/Etc.) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 15 (Property Description) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 16 (Value of Property) (mandatory):
Numeric value in whole dollars
Data Element 17 (Date Recovered) (conditional, if property recovered):
YYYYMMDD
Data Element 23 (Victim Sequence Number) (mandatory):
001-999 (unique number for each victim)
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
120 = Robbery
Data Element 25 (Type of Victim) (mandatory):
I = Individual
B = Business
F = Financial Institution
G = Government
R = Religious Organization
S = Society/Public
O = Other
U = Unknown
Data Element 26 (Age of Victim) (mandatory, if individual victim):
00 = Unknown
01-98 = Years Old
99 = Over 98 Years Old
NN = Under 24 Hours (Neonate)
NB = 1-6 Days Old (Newborn)
BB = 7-364 Days Old (Baby)
Data Element 27 (Sex of Victim) (mandatory, if individual victim):
M = Male
F = Female
U = Unknown
Data Element 28 (Race of Victim) (mandatory, if individual victim):
W = White
B = Black or African American
I = American Indian or Alaska Native
A = Asian
P = Native Hawaiian or Other Pacific Islander
U = Unknown
Data Element 29 (Ethnicity of Victim) (optional, if individual victim):
H = Hispanic or Latino
N = Not Hispanic or Latino
U = Unknown
Data Element 30 (Resident Status of Victim) (optional, if individual victim):
R = Resident
N = Nonresident
U = Unknown
Data Element 33 (Type Injury) (mandatory, if individual victim):
N = None
B = Apparent Broken Bones
I = Possible Internal Injury
L = Severe Laceration
M = Apparent Minor Injury
O = Other Major Injury
T = Loss of Teeth
U = Unconsciousness
Data Element 34 (Offender Number to be Related) (mandatory, if individual victim):
00 = Unknown
01-99 = Offender Sequence Number
Data Element 35 (Relationship of Victim to Offender) (mandatory, for each offender in Data Element 34, if individual victim):
SE = Spouse
CS = Common-Law Spouse
PA = Parent
SB = Sibling
CH = Child
GP = Grandparent
GC = Grandchild
IL = In-Law
SP = Stepparent
SC = Stepchild
SS = Stepsibling
OF = Other Family Member
AQ = Acquaintance
FR = Friend
NE = Neighbor
BE = Babysittee (Baby)
BG = Boyfriend/Girlfriend
CF = Child of Boyfriend/Girlfriend
XS = Ex-Spouse
EE = Employee
ER = Employer
OK = Otherwise Known
RU = Relationship Unknown
ST = Stranger
VO = Victim Was Offender
XR = Ex-Relationship
Data Element 36 (Offender Sequence Number) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 37 (Age of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 38 (Sex of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39 (Race of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39A (Ethnicity of Offender) (optional):
Same as Burglary to Commercial Buildings (220)
II. Crimes Against Persons
These offenses involve individual victims and are counted as one offense per victim. A. Sex Offenses
Rape (11A)
Definition: The penetration, no matter how slight, of the vagina or anus with any body part or object, or oral penetration by a sex organ of another person, without the consent of the victim. Data Elements and Sub-Elements:
Data Element 1 (ORI) (mandatory):
9-character ORI code
Data Element 2 (Incident Number) (mandatory):
Up to 12-character incident number
Data Element 2A (Cargo Theft) (mandatory):
Y = Yes
N = No
Data Element 3 (Incident Date) (mandatory):
YYYYMMDD
Data Element 4 (Cleared Exceptionally) (mandatory if cleared):
Same as Burglary to Commercial Buildings (220)
Data Element 5 (Exceptional Clearance Date) (conditional, if cleared exceptionally):
YYYYMMDD
Data Element 6 (UCR Offense Code) (mandatory):
11A = Rape
Data Element 7 (Offense Attempted/Completed) (mandatory):
A = Attempted
C = Completed
Data Element 8 (Offender Suspected of Using) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 8A (Bias Motivation) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 9 (Location Type) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 12 (Type Criminal Activity/Gang Information) (mandatory, up to three):
Same as Burglary to Commercial Buildings (220)
Data Element 13 (Type Weapon/Force Involved) (mandatory):
Same as Robbery (120)
Data Element 23 (Victim Sequence Number) (mandatory):
001-999
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11A = Rape
Data Element 25 (Type of Victim) (mandatory):
I = Individual
S = Society/Public
Data Element 25A (Type of Officer Activity/Circumstance) (conditional, if victim is a law enforcement officer):
01 = Responding to Disturbance Call
02 = Burglary in Progress/Pursuing Burglary Suspect
03 = Robbery in Progress/Pursuing Robbery Suspect
04 = Attempting Other Arrest
05 = Civil Disorder
06 = Handling/Transporting/Custody of Prisoner
07 = Investigating Suspicious Person/Circumstance
08 = Ambush-No Warning
09 = Mentally Deranged Assailant
10 = Traffic Pursuit/Stop
11 = All Other
Data Element 25B (Officer Assignment Type) (conditional, if victim is a law enforcement officer):
F = Two-Officer Vehicle
G = One-Officer Vehicle (Alone)
H = One-Officer Vehicle (Assisted)
I = Detective or Special Assignment (Alone)
J = Detective or Special Assignment (Assisted)
K = Other (Alone)
L = Other (Assisted)
Data Element 25C (Officer - ORI Other Jurisdiction) (conditional, if victim is a law enforcement officer from another jurisdiction):
9-character ORI code
Data Element 26 (Age of Victim) (mandatory):
Same as Robbery (120)
Data Element 27 (Sex of Victim) (mandatory):
Same as Robbery (120)
Data Element 28 (Race of Victim) (mandatory):
Same as Robbery (120)
Data Element 29 (Ethnicity of Victim) (optional):
Same as Robbery (120)
Data Element 30 (Resident Status of Victim) (optional):
Same as Robbery (120)
Data Element 33 (Type Injury) (mandatory):
Same as Robbery (120)
Data Element 34 (Offender Number to be Related) (mandatory):
Same as Robbery (120)
Data Element 35 (Relationship of Victim to Offender) (mandatory, for each offender in Data Element 34):
Same as Robbery (120)
Data Element 36 (Offender Sequence Number) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 37 (Age of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 38 (Sex of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39 (Race of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39A (Ethnicity of Offender) (optional):
Same as Burglary to Commercial Buildings (220)
Sodomy (11B)
Definition: Oral or anal sexual intercourse with another person, without the consent of the victim, including cases where the victim is incapable of giving consent because of his/her age or because of his/her temporary or permanent mental or physical incapacity. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
11B = Sodomy
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11B = Sodomy
Sexual Assault With An Object (11C)
Definition: The use of an object or instrument to unlawfully penetrate, however slightly, the genital or anal opening of the body of another person, without the consent of the victim, including cases where the victim is incapable of giving consent because of his/her age or because of his/her temporary or permanent mental or physical incapacity. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
11C = Sexual Assault With An Object
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11C = Sexual Assault With An Object
Fondling (11D)
Definition: The touching of the private body parts of another person for the purpose of sexual gratification, without the consent of the victim, including cases where the victim is incapable of giving consent because of his/her age or because of his/her temporary or permanent mental or physical incapacity. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
11D = Fondling
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11D = Fondling
Incest (36A)
Definition: Nonforcible sexual intercourse between persons who are related to each other within the degrees wherein marriage is prohibited by law. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
36A = Incest
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
36A = Incest
Statutory Rape (36B)
Definition: Nonforcible sexual intercourse with a person who is under the statutory age of consent. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
36B = Statutory Rape
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
36B = Statutory Rape
Notes
Clarification on Burglary of a Motor Vehicle: The NIBRS manual classifies break-ins to motor vehicles as Theft From Motor Vehicle (23F) under Larceny/Theft Offenses, not as burglary, because motor vehicles (unless permanently fixed as a residence or office) do not meet the NIBRS definition of a "structure" for burglary. If the intent was to refer to actual burglary of a motor vehicle used as a permanent dwelling, it would fall under Burglary (220) with appropriate location and property codes. Mandatory vs. Conditional vs. Optional Data Elements: Mandatory elements are required for valid data submission. Conditional elements depend on circumstances (e.g., property recovery, law enforcement officer victim). Optional elements are at the agency’s discretion. Dropdown Menus: The numbered lists for each data element’s sub-elements are designed for direct implementation into dropdown menus for standardized data entry systems. Date Format: All date fields (e.g., Incident Date, Exceptional Clearance Date, Date Recovered) must be in YYYYMMDD format. Numeric Fields: Fields like Number of Premises Entered, Number of Stolen/Recovered Motor Vehicles, and Value of Property require numeric inputs in whole numbers. Victim Data for Property Crimes: Most property crimes (except Robbery) do not require victim data unless an individual is directly affected (e.g., a business or society as a victim). Robbery includes victim data due to its violent nature. Weekly Reporting: The listed elements and sub-elements cover all required data for weekly NIBRS reporting, ensuring comprehensive and standardized data collection for the specified crimes. Outline of Specified NIBRS Crimes, Elements, and Sub-Elements
I. Crimes Against Property
A. Burglary/Breaking and Entering
1. Burglary to Commercial Buildings (220)
Definition: The unlawful entry into a commercial building or other structure (e.g., office, store, warehouse) with the intent to commit a felony or a theft. Data Elements and Sub-Elements:
Data Element 1 (ORI) (mandatory):
9-character ORI code
Data Element 2 (Incident Number) (mandatory):
Up to 12-character incident number
Data Element 2A (Cargo Theft) (mandatory):
Y = Yes
N = No
Data Element 3 (Incident Date) (mandatory):
YYYYMMDD (Year, Month, Day)
Data Element 4 (Cleared Exceptionally) (mandatory if cleared):
A = Death of Offender
B = Prosecution Declined
C = In Custody of Other Jurisdiction
D = Victim Refused to Cooperate
E = Juvenile/No Custody
N = Not Applicable
Data Element 5 (Exceptional Clearance Date) (conditional, if cleared exceptionally):
YYYYMMDD
Data Element 6 (UCR Offense Code) (mandatory):
220 = Burglary/Breaking and Entering
Data Element 7 (Offense Attempted/Completed) (mandatory):
A = Attempted
C = Completed
Data Element 8 (Offender Suspected of Using) (mandatory):
A = Alcohol
C = Computer Equipment (Handheld Devices)
D = Drugs/Narcotics
N = Not Applicable
Data Element 8A (Bias Motivation) (mandatory):
11 = Anti-White
12 = Anti-Black or African American
13 = Anti-American Indian or Alaska Native
14 = Anti-Asian
15 = Anti-Native Hawaiian or Other Pacific Islander
16 = Anti-Multiple Races, Group
21 = Anti-Arab
22 = Anti-Hispanic or Latino
23 = Anti-Other Race/Ethnicity/Ancestry
31 = Anti-Jewish
32 = Anti-Catholic
33 = Anti-Protestant
34 = Anti-Islamic (Muslim)
35 = Anti-Other Religion
36 = Anti-Multi-Religious Group
37 = Anti-Atheist/Agnostic
38 = Anti-Mormon
39 = Anti-Jehovah’s Witness
41 = Anti-Eastern Orthodox
42 = Anti-Other Christian
43 = Anti-Buddhist
44 = Anti-Hindu
45 = Anti-Sikh
51 = Anti-Gay (Male)
52 = Anti-Lesbian
53 = Anti-Lesbian, Gay, Bisexual, or Transgender (Mixed Group)
54 = Anti-Transgender
55 = Anti-Gender Non-Conforming
61 = Anti-Physical Disability
62 = Anti-Mental Disability
71 = Anti-Male
72 = Anti-Female
88 = None (No Bias)
99 = Unknown (Bias Unknown)
Data Element 9 (Location Type) (mandatory):
01 = Air/Bus/Train Terminal
02 = Bank/Savings and Loan
03 = Bar/Nightclub
04 = Church/Synagogue/Temple/Mosque
05 = Commercial/Office Building
06 = Construction Site
07 = Convenience Store
08 = Department/Discount Store
09 = Drug Store/Doctor’s Office/Hospital
10 = Field/Woods
11 = Government/Public Building
12 = Grocery/Supermarket
13 = Highway/Road/Alley/Street/Sidewalk
14 = Hotel/Motel/Etc. 15 = Jail/Prison/Penitentiary/Corrections Facility
16 = Lake/Waterway/Beach
17 = Liquor Store
18 = Parking Lot/Garage/Drop Lot
19 = Rental Storage Facility
20 = Residence/Home
21 = Restaurant
22 = School/College
23 = Service/Gas Station
24 = Specialty Store
25 = Other/Unknown
37 = Abandoned/Condemned Structure
38 = Amusement Park
39 = Arena/Stadium/Fairgrounds/Coliseum
40 = ATM Separate from Bank
41 = Auto Dealership New/Used
42 = Camp/Campground
44 = Daycare Facility
45 = Dock/Wharf/Freight/Modal Terminal
46 = Farm Facility
47 = Gambling Facility/Casino/Race Track
48 = Industrial Site
49 = Military Installation
50 = Park/Playground
51 = Rest Area
52 = School-College/University
53 = School-Elementary/Secondary
54 = Shelter-Mission/Homeless
55 = Shopping Mall
56 = Tribal Lands
57 = Community Center
58 = Cyberspace
Data Element 10 (Number of Premises Entered) (mandatory):
01-99
Data Element 11 (Method of Entry) (mandatory):
F = Forced Entry
N = No Forced Entry
Data Element 12 (Type Criminal Activity/Gang Information) (mandatory, up to three):
B = Buying/Receiving
C = Cultivating/Manufacturing/Publishing
D = Distributing/Selling
E = Exploiting Children
J = Juvenile Gang
O = Operating/Promoting/Assisting
P = Possessing/Concealing
T = Transporting/Transmitting/Importing
U = Using/Consuming
G = Other Gang
N = None/Unknown
Data Element 14 (Type Property Loss/Etc.) (mandatory):
1 = None
2 = Burned
3 = Counterfeited/Forged
4 = Damaged/Destroyed
5 = Recovered
6 = Seized
7 = Stolen/Etc. 8 = Unknown
Data Element 15 (Property Description) (mandatory):
01 = Aircraft
02 = Alcohol
03 = Automobile
04 = Bicycle
05 = Bus
06 = Clothes/Furs
07 = Computer Hardware/Software
08 = Consumable Goods
09 = Credit/Debit Cards
10 = Drugs/Narcotics
11 = Drug/Narcotic Equipment
12 = Farm Equipment
13 = Firearms
14 = Gambling Equipment
15 = Heavy Construction/Industrial Equipment
16 = Household Goods
17 = Jewelry/Precious Metals/Gems
18 = Livestock
19 = Merchandise
20 = Money
21 = Negotiable Instruments
22 = Non-Negotiable Instruments
23 = Office-Type Equipment
24 = Other Motor Vehicles
25 = Purses/Handbags/Wallets
26 = Radios/TVs/VCRs/DVD Players
27 = Recordings-Audio/Video
28 = Recreational Vehicles
29 = Structures-Single Occupancy Dwellings
30 = Structures-Other Dwellings
31 = Structures-Other Commercial/Business
32 = Structures-Industrial/Manufacturing
33 = Structures-Public/Community
34 = Structures-Storage
35 = Structures-Other
36 = Tools
37 = Trucks
38 = Vehicle Parts/Accessories
39 = Watercraft
41 = Aircraft Parts/Accessories
42 = Artistic Supplies/Accessories
43 = Building Materials
44 = Camping/Hunting/Fishing Equipment/Supplies
45 = Chemicals
46 = Collections/Collectibles
47 = Crops
48 = Documents/Personal or Business
49 = Explosives
59 = Firearm Accessories
60 = Fuel
61 = Identity Documents
62 = Identity-Intangible
64 = Law Enforcement Equipment
65 = Lawn/Yard/Garden Equipment
66 = Logging Equipment
67 = Medical/Medical Lab Equipment
68 = Metals, Non-Precious
69 = Musical Instruments
70 = Pets
71 = Photographic/Optical Equipment
72 = Portable Electronic Communications
73 = Recreational/Sports Equipment
74 = Scrap Metal
75 = Tobacco
76 = Trailers
77 = Watercraft Equipment/Parts/Accessories
78 = Weapons-Other
88 = Pending Inventory (Unknown)
99 = Other
Data Element 16 (Value of Property) (mandatory):
Numeric value in whole dollars
Data Element 17 (Date Recovered) (conditional, if property recovered):
YYYYMMDD
Data Element 36 (Offender Sequence Number) (mandatory):
00 = Unknown
01-99 = Offender Sequence Number
Data Element 37 (Age of Offender) (mandatory):
00 = Unknown
01-98 = Years Old
99 = Over 98 Years Old
Data Element 38 (Sex of Offender) (mandatory):
M = Male
F = Female
U = Unknown
Data Element 39 (Race of Offender) (mandatory):
W = White
B = Black or African American
I = American Indian or Alaska Native
A = Asian
P = Native Hawaiian or Other Pacific Islander
U = Unknown
Data Element 39A (Ethnicity of Offender) (optional):
H = Hispanic or Latino
N = Not Hispanic or Latino
U = Unknown
2. Burglary to Residential Structures (220)
Definition: The unlawful entry into a residential structure (e.g., house, apartment, condominium) with the intent to commit a felony or a theft. Data Elements and Sub-Elements:
Identical to Burglary to Commercial Buildings (220), except the Data Element 9 (Location Type) will typically be:
20 = Residence/Home
29 = Structures-Single Occupancy Dwellings (in Data Element 15, if applicable)
30 = Structures-Other Dwellings (in Data Element 15, if applicable)
B. Larceny/Theft Offenses
1. Theft From Motor Vehicle (23F)
Definition: The unlawful taking of property from within a motor vehicle, not constituting burglary. Data Elements and Sub-Elements:
Same as Burglary to Commercial Buildings (220), except:
Data Element 6 (UCR Offense Code) (mandatory):
23F = Theft From Motor Vehicle
Data Element 10 (Number of Premises Entered): Not applicable
Data Element 11 (Method of Entry): Not applicable
C. Motor Vehicle Theft
1. Motor Vehicle Theft (240)
Definition: The theft or attempted theft of a motor vehicle. Data Elements and Sub-Elements:
Same as Burglary to Commercial Buildings (220), except:
Data Element 6 (UCR Offense Code) (mandatory):
240 = Motor Vehicle Theft
Data Element 10 (Number of Premises Entered): Not applicable
Data Element 11 (Method of Entry): Not applicable
Data Element 18 (Number of Stolen Motor Vehicles) (mandatory):
00-99
Data Element 19 (Number of Recovered Motor Vehicles) (conditional, if recovered):
00-99
D. Robbery
1. Robbery (120)
Definition: The taking or attempting to take anything of value from the care, custody, or control of a person or persons by force or threat of force or violence and/or by putting the victim in fear.

Data Elements and Sub-Elements:
Data Element 1 (ORI) (mandatory):
9-character ORI code
Data Element 2 (Incident Number) (mandatory):
Up to 12-character incident number
Data Element 2A (Cargo Theft) (mandatory):
Y = Yes
N = No
Data Element 3 (Incident Date) (mandatory):
YYYYMMDD
Data Element 4 (Cleared Exceptionally) (mandatory if cleared):
Same as Burglary to Commercial Buildings (220)
Data Element 5 (Exceptional Clearance Date) (conditional, if cleared exceptionally):
YYYYMMDD
Data Element 6 (UCR Offense Code) (mandatory):
120 = Robbery
Data Element 7 (Offense Attempted/Completed) (mandatory):
A = Attempted
C = Completed
Data Element 8 (Offender Suspected of Using) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 8A (Bias Motivation) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 9 (Location Type) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 12 (Type Criminal Activity/Gang Information) (mandatory, up to three):
Same as Burglary to Commercial Buildings (220)
Data Element 13 (Type Weapon/Force Involved) (mandatory):
11 = Firearm (Unspecified)
12 = Handgun
13 = Rifle
14 = Shotgun
15 = Other Firearm
20 = Knife/Cutting Instrument
30 = Blunt Object
35 = Motor Vehicle/Vessel
40 = Personal Weapons (Hands, Feet, Teeth, Etc.) 50 = Poison
60 = Explosives
65 = Fire/Incendiary Device
70 = Drugs/Narcotics/Sleeping Pills
85 = Asphyxiation
90 = Other
95 = Unknown
99 = None
Data Element 14 (Type Property Loss/Etc.) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 15 (Property Description) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 16 (Value of Property) (mandatory):
Numeric value in whole dollars
Data Element 17 (Date Recovered) (conditional, if property recovered):
YYYYMMDD
Data Element 23 (Victim Sequence Number) (mandatory):
001-999 (unique number for each victim)
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
120 = Robbery
Data Element 25 (Type of Victim) (mandatory):
I = Individual
B = Business
F = Financial Institution
G = Government
R = Religious Organization
S = Society/Public
O = Other
U = Unknown
Data Element 26 (Age of Victim) (mandatory, if individual victim):
00 = Unknown
01-98 = Years Old
99 = Over 98 Years Old
NN = Under 24 Hours (Neonate)
NB = 1-6 Days Old (Newborn)
BB = 7-364 Days Old (Baby)
Data Element 27 (Sex of Victim) (mandatory, if individual victim):
M = Male
F = Female
U = Unknown
Data Element 28 (Race of Victim) (mandatory, if individual victim):
W = White
B = Black or African American
I = American Indian or Alaska Native
A = Asian
P = Native Hawaiian or Other Pacific Islander
U = Unknown
Data Element 29 (Ethnicity of Victim) (optional, if individual victim):
H = Hispanic or Latino
N = Not Hispanic or Latino
U = Unknown
Data Element 30 (Resident Status of Victim) (optional, if individual victim):
R = Resident
N = Nonresident
U = Unknown
Data Element 33 (Type Injury) (mandatory, if individual victim):
N = None
B = Apparent Broken Bones
I = Possible Internal Injury
L = Severe Laceration
M = Apparent Minor Injury
O = Other Major Injury
T = Loss of Teeth
U = Unconsciousness
Data Element 34 (Offender Number to be Related) (mandatory, if individual victim):
00 = Unknown
01-99 = Offender Sequence Number
Data Element 35 (Relationship of Victim to Offender) (mandatory, for each offender in Data Element 34, if individual victim):
SE = Spouse
CS = Common-Law Spouse
PA = Parent
SB = Sibling
CH = Child
GP = Grandparent
GC = Grandchild
IL = In-Law
SP = Stepparent
SC = Stepchild
SS = Stepsibling
OF = Other Family Member
AQ = Acquaintance
FR = Friend
NE = Neighbor
BE = Babysittee (Baby)
BG = Boyfriend/Girlfriend
CF = Child of Boyfriend/Girlfriend
XS = Ex-Spouse
EE = Employee
ER = Employer
OK = Otherwise Known
RU = Relationship Unknown
ST = Stranger
VO = Victim Was Offender
XR = Ex-Relationship
Data Element 36 (Offender Sequence Number) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 37 (Age of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 38 (Sex of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39 (Race of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39A (Ethnicity of Offender) (optional):
Same as Burglary to Commercial Buildings (220)
II. Crimes Against Persons
A. Sex Offenses
1. Rape (11A)
Definition: The penetration, no matter how slight, of the vagina or anus with any body part or object, or oral penetration by a sex organ of another person, without the consent of the victim. Data Elements and Sub-Elements:
Data Element 1 (ORI) (mandatory):
9-character ORI code
Data Element 2 (Incident Number) (mandatory):
Up to 12-character incident number
Data Element 2A (Cargo Theft) (mandatory):
Y = Yes
N = No
Data Element 3 (Incident Date) (mandatory):
YYYYMMDD
Data Element 4 (Cleared Exceptionally) (mandatory if cleared):
Same as Burglary to Commercial Buildings (220)
Data Element 5 (Exceptional Clearance Date) (conditional, if cleared exceptionally):
YYYYMMDD
Data Element 6 (UCR Offense Code) (mandatory):
11A = Rape
Data Element 7 (Offense Attempted/Completed) (mandatory):
A = Attempted
C = Completed
Data Element 8 (Offender Suspected of Using) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 8A (Bias Motivation) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 9 (Location Type) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 12 (Type Criminal Activity/Gang Information) (mandatory, up to three):
Same as Burglary to Commercial Buildings (220)
Data Element 13 (Type Weapon/Force Involved) (mandatory):
Same as Robbery (120)
Data Element 23 (Victim Sequence Number) (mandatory):
001-999
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11A = Rape
Data Element 25 (Type of Victim) (mandatory):
I = Individual
S = Society/Public
Data Element 25A (Type of Officer Activity/Circumstance) (conditional, if victim is a law enforcement officer):
01 = Responding to Disturbance Call
02 = Burglary in Progress/Pursuing Burglary Suspect
03 = Robbery in Progress/Pursuing Robbery Suspect
04 = Attempting Other Arrest
05 = Civil Disorder
06 = Handling/Transporting/Custody of Prisoner
07 = Investigating Suspicious Person/Circumstance
08 = Ambush-No Warning
09 = Mentally Deranged Assailant
10 = Traffic Pursuit/Stop
11 = All Other
Data Element 25B (Officer Assignment Type) (conditional, if victim is a law enforcement officer):
F = Two-Officer Vehicle
G = One-Officer Vehicle (Alone)
H = One-Officer Vehicle (Assisted)
I = Detective or Special Assignment (Alone)
J = Detective or Special Assignment (Assisted)
K = Other (Alone)
L = Other (Assisted)
Data Element 25C (Officer - ORI Other Jurisdiction) (conditional, if victim is a law enforcement officer from another jurisdiction):
9-character ORI code
Data Element 26 (Age of Victim) (mandatory):
Same as Robbery (120)
Data Element 27 (Sex of Victim) (mandatory):
Same as Robbery (120)
Data Element 28 (Race of Victim) (mandatory):
Same as Robbery (120)
Data Element 29 (Ethnicity of Victim) (optional):
Same as Robbery (120)
Data Element 30 (Resident Status of Victim) (optional):
Same as Robbery (120)
Data Element 33 (Type Injury) (mandatory):
Same as Robbery (120)
Data Element 34 (Offender Number to be Related) (mandatory):
Same as Robbery (120)
Data Element 35 (Relationship of Victim to Offender) (mandatory, for each offender in Data Element 34):
Same as Robbery (120)
Data Element 36 (Offender Sequence Number) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 37 (Age of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 38 (Sex of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39 (Race of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39A (Ethnicity of Offender) (optional):
Same as Burglary to Commercial Buildings (220)
2. Sodomy (11B)
Definition: Oral or anal sexual intercourse with another person, without the consent of the victim, including cases where the victim is incapable of giving consent because of his/her age or because of his/her temporary or permanent mental or physical incapacity. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
11B = Sodomy
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11B = Sodomy
3. Sexual Assault With An Object (11C)
Definition: The use of an object or instrument to unlawfully penetrate, however slightly, the genital or anal opening of the body of another person, without the consent of the victim, including cases where the victim is incapable of giving consent because of his/her age or because of his/her temporary or permanent mental or physical incapacity. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
11C = Sexual Assault With An Object
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11C = Sexual Assault With An Object
4. Fondling (11D)
Definition: The touching of the private body parts of another person for the purpose of sexual gratification, without the consent of the victim, including cases where the victim is incapable of giving consent because of his/her age or because of his/her temporary or permanent mental or physical incapacity. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
11D = Fondling
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11D = Fondling
5. Incest (36A)
Definition: Nonforcible sexual intercourse between persons who are related to each other within the degrees wherein marriage is prohibited by law. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
36A = Incest
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
36A = Incest
6. Statutory Rape (36B)
Definition: Nonforcible sexual intercourse with a person who is under the statutory age of consent. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
36B = Statutory Rape
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
36B = Statutory Rape
Notes
Clarification on Burglary of a Motor Vehicle: The NIBRS manual classifies break-ins to motor vehicles as Theft From Motor Vehicle (23F) under Larceny/Theft Offenses, not as burglary, because motor vehicles (unless permanently fixed as a residence or office) do not meet the NIBRS definition of a "structure" for burglary. If the intent was to refer to actual burglary of a motor vehicle used as a permanent dwelling, it would fall under Burglary (220) with appropriate location and property codes. Mandatory vs. Conditional vs. Optional Data Elements: Mandatory elements are required for valid data submission. Conditional elements depend on circumstances (e.g., property recovery, law enforcement officer victim). Optional elements are at the agency’s discretion. Dropdown Menus: The numbered lists for each data element’s sub-elements are designed for direct implementation into dropdown menus for standardized data entry systems. Date Format: All date fields (e.g., Incident Date, Exceptional Clearance Date, Date Recovered) must be in YYYYMMDD format. Numeric Fields: Fields like Number of Premises Entered, Number of Stolen/Recovered Motor Vehicles, and Value of Property require numeric inputs in whole numbers. Victim Data for Property Crimes: Most property crimes (except Robbery) do not require victim data unless an individual is directly affected (e.g., a business or society as a victim). Robbery includes victim data due to its violent nature. Weekly Reporting: The listed elements and sub-elements cover all required data for weekly NIBRS reporting, ensuring comprehensive and standardized data collection for the specified crimes. Below is a comprehensive outline of the specified crimes from the 2019 National Incident-Based Reporting System (NIBRS) User Manual, focusing on Burglary to Commercial Buildings, Burglary to Residential Structures, Burglary of a Motor Vehicle, Theft of Motor Vehicle, Robbery, and all Sexual Offenses. Each crime includes its NIBRS offense code, definition, and the mandatory, conditional, and optional data elements and sub-elements (data values) required for entry into the NIBRS database. The sub-elements are presented in numbered lists to facilitate the creation of dropdown menus for standardized data entry, as requested. The outline adheres to the formal tone and structured format specified, ensuring clarity and precision. Note that "Burglary of a Motor Vehicle" is interpreted as "Theft From Motor Vehicle" (23F), as NIBRS does not classify motor vehicle break-ins as burglary but as a larceny/theft offense, unless specified otherwise. Outline of Specified NIBRS Crimes, Elements, and Sub-Elements
I. Crimes Against Property
These offenses aim to obtain money, property, or some other benefit and are counted as one offense per distinct operation, except for Motor Vehicle Theft, which is one offense per stolen vehicle. A. Burglary/Breaking and Entering
Burglary to Commercial Buildings (220)
Definition: The unlawful entry into a commercial building or other structure (e.g., office, store, warehouse) with the intent to commit a felony or a theft. Data Elements and Sub-Elements:
Data Element 1 (ORI) (mandatory):
9-character ORI code
Data Element 2 (Incident Number) (mandatory):
Up to 12-character incident number
Data Element 2A (Cargo Theft) (mandatory):
Y = Yes
N = No
Data Element 3 (Incident Date) (mandatory):
YYYYMMDD (Year, Month, Day)
Data Element 4 (Cleared Exceptionally) (mandatory if cleared):
A = Death of Offender
B = Prosecution Declined
C = In Custody of Other Jurisdiction
D = Victim Refused to Cooperate
E = Juvenile/No Custody
N = Not Applicable
Data Element 5 (Exceptional Clearance Date) (conditional, if cleared exceptionally):
YYYYMMDD
Data Element 6 (UCR Offense Code) (mandatory):
220 = Burglary/Breaking and Entering
Data Element 7 (Offense Attempted/Completed) (mandatory):
A = Attempted
C = Completed
Data Element 8 (Offender Suspected of Using) (mandatory):
A = Alcohol
C = Computer Equipment (Handheld Devices)
D = Drugs/Narcotics
N = Not Applicable
Data Element 8A (Bias Motivation) (mandatory):
11 = Anti-White
12 = Anti-Black or African American
13 = Anti-American Indian or Alaska Native
14 = Anti-Asian
15 = Anti-Native Hawaiian or Other Pacific Islander
16 = Anti-Multiple Races, Group
21 = Anti-Arab
22 = Anti-Hispanic or Latino
23 = Anti-Other Race/Ethnicity/Ancestry
31 = Anti-Jewish
32 = Anti-Catholic
33 = Anti-Protestant
34 = Anti-Islamic (Muslim)
35 = Anti-Other Religion
36 = Anti-Multi-Religious Group
37 = Anti-Atheist/Agnostic
38 = Anti-Mormon
39 = Anti-Jehovah’s Witness
41 = Anti-Eastern Orthodox
42 = Anti-Other Christian
43 = Anti-Buddhist
44 = Anti-Hindu
45 = Anti-Sikh
51 = Anti-Gay (Male)
52 = Anti-Lesbian
53 = Anti-Lesbian, Gay, Bisexual, or Transgender (Mixed Group)
54 = Anti-Transgender
55 = Anti-Gender Non-Conforming
61 = Anti-Physical Disability
62 = Anti-Mental Disability
71 = Anti-Male
72 = Anti-Female
88 = None (No Bias)
99 = Unknown (Bias Unknown)
Data Element 9 (Location Type) (mandatory):
01 = Air/Bus/Train Terminal
02 = Bank/Savings and Loan
03 = Bar/Nightclub
04 = Church/Synagogue/Temple/Mosque
05 = Commercial/Office Building
06 = Construction Site
07 = Convenience Store
08 = Department/Discount Store
09 = Drug Store/Doctor’s Office/Hospital
10 = Field/Woods
11 = Government/Public Building
12 = Grocery/Supermarket
13 = Highway/Road/Alley/Street/Sidewalk
14 = Hotel/Motel/Etc. 15 = Jail/Prison/Penitentiary/Corrections Facility
16 = Lake/Waterway/Beach
17 = Liquor Store
18 = Parking Lot/Garage/Drop Lot
19 = Rental Storage Facility
20 = Residence/Home
21 = Restaurant
22 = School/College
23 = Service/Gas Station
24 = Specialty Store
25 = Other/Unknown
37 = Abandoned/Condemned Structure
38 = Amusement Park
39 = Arena/Stadium/Fairgrounds/Coliseum
40 = ATM Separate from Bank
41 = Auto Dealership New/Used
42 = Camp/Campground
44 = Daycare Facility
45 = Dock/Wharf/Freight/Modal Terminal
46 = Farm Facility
47 = Gambling Facility/Casino/Race Track
48 = Industrial Site
49 = Military Installation
50 = Park/Playground
51 = Rest Area
52 = School-College/University
53 = School-Elementary/Secondary
54 = Shelter-Mission/Homeless
55 = Shopping Mall
56 = Tribal Lands
57 = Community Center
58 = Cyberspace
Data Element 10 (Number of Premises Entered) (mandatory):
01-99
Data Element 11 (Method of Entry) (mandatory):
F = Forced Entry
N = No Forced Entry
Data Element 12 (Type Criminal Activity/Gang Information) (mandatory, up to three):
B = Buying/Receiving
C = Cultivating/Manufacturing/Publishing
D = Distributing/Selling
E = Exploiting Children
J = Juvenile Gang
O = Operating/Promoting/Assisting
P = Possessing/Concealing
T = Transporting/Transmitting/Importing
U = Using/Consuming
G = Other Gang
N = None/Unknown
Data Element 14 (Type Property Loss/Etc.) (mandatory):
1 = None
2 = Burned
3 = Counterfeited/Forged
4 = Damaged/Destroyed
5 = Recovered
6 = Seized
7 = Stolen/Etc. 8 = Unknown
Data Element 15 (Property Description) (mandatory):
01 = Aircraft
02 = Alcohol
03 = Automobile
04 = Bicycle
05 = Bus
06 = Clothes/Furs
07 = Computer Hardware/Software
08 = Consumable Goods
09 = Credit/Debit Cards
10 = Drugs/Narcotics
11 = Drug/Narcotic Equipment
12 = Farm Equipment
13 = Firearms
14 = Gambling Equipment
15 = Heavy Construction/Industrial Equipment
16 = Household Goods
17 = Jewelry/Precious Metals/Gems
18 = Livestock
19 = Merchandise
20 = Money
21 = Negotiable Instruments
22 = Non-Negotiable Instruments
23 = Office-Type Equipment
24 = Other Motor Vehicles
25 = Purses/Handbags/Wallets
26 = Radios/TVs/VCRs/DVD Players
27 = Recordings-Audio/Video
28 = Recreational Vehicles
29 = Structures-Single Occupancy Dwellings
30 = Structures-Other Dwellings
31 = Structures-Other Commercial/Business
32 = Structures-Industrial/Manufacturing
33 = Structures-Public/Community
34 = Structures-Storage
35 = Structures-Other
36 = Tools
37 = Trucks
38 = Vehicle Parts/Accessories
39 = Watercraft
41 = Aircraft Parts/Accessories
42 = Artistic Supplies/Accessories
43 = Building Materials
44 = Camping/Hunting/Fishing Equipment/Supplies
45 = Chemicals
46 = Collections/Collectibles
47 = Crops
48 = Documents/Personal or Business
49 = Explosives
59 = Firearm Accessories
60 = Fuel
61 = Identity Documents
62 = Identity-Intangible
64 = Law Enforcement Equipment
65 = Lawn/Yard/Garden Equipment
66 = Logging Equipment
67 = Medical/Medical Lab Equipment
68 = Metals, Non-Precious
69 = Musical Instruments
70 = Pets
71 = Photographic/Optical Equipment
72 = Portable Electronic Communications
73 = Recreational/Sports Equipment
74 = Scrap Metal
75 = Tobacco
76 = Trailers
77 = Watercraft Equipment/Parts/Accessories
78 = Weapons-Other
88 = Pending Inventory (Unknown)
99 = Other
Data Element 16 (Value of Property) (mandatory):
Numeric value in whole dollars
Data Element 17 (Date Recovered) (conditional, if property recovered):
YYYYMMDD
Data Element 36 (Offender Sequence Number) (mandatory):
00 = Unknown
01-99 = Offender Sequence Number
Data Element 37 (Age of Offender) (mandatory):
00 = Unknown
01-98 = Years Old
99 = Over 98 Years Old
Data Element 38 (Sex of Offender) (mandatory):
M = Male
F = Female
U = Unknown
Data Element 39 (Race of Offender) (mandatory):
W = White
B = Black or African American
I = American Indian or Alaska Native
A = Asian
P = Native Hawaiian or Other Pacific Islander
U = Unknown
Data Element 39A (Ethnicity of Offender) (optional):
H = Hispanic or Latino
N = Not Hispanic or Latino
U = Unknown
Burglary to Residential Structures (220)
Definition: The unlawful entry into a residential structure (e.g., house, apartment, condominium) with the intent to commit a felony or a theft. Data Elements and Sub-Elements:
Identical to Burglary to Commercial Buildings (220), except the Data Element 9 (Location Type) will typically be:
20 = Residence/Home
29 = Structures-Single Occupancy Dwellings (in Data Element 15, if applicable)
30 = Structures-Other Dwellings (in Data Element 15, if applicable)
B. Larceny/Theft Offenses
Theft From Motor Vehicle (23F)
Definition: The unlawful taking of property from within a motor vehicle, not constituting burglary. Data Elements and Sub-Elements:
Same as Burglary to Commercial Buildings (220), except:
Data Element 6 (UCR Offense Code) (mandatory):
23F = Theft From Motor Vehicle
Data Element 10 (Number of Premises Entered): Not applicable
Data Element 11 (Method of Entry): Not applicable
C. Motor Vehicle Theft
Motor Vehicle Theft (240)
Definition: The theft or attempted theft of a motor vehicle. Data Elements and Sub-Elements:
Same as Burglary to Commercial Buildings (220), except:
Data Element 6 (UCR Offense Code) (mandatory):
240 = Motor Vehicle Theft
Data Element 10 (Number of Premises Entered): Not applicable
Data Element 11 (Method of Entry): Not applicable
Data Element 18 (Number of Stolen Motor Vehicles) (mandatory):
00-99
Data Element 19 (Number of Recovered Motor Vehicles) (conditional, if recovered):
00-99
D. Robbery
Robbery (120)
Definition: The taking or attempting to take anything of value from the care, custody, or control of a person or persons by force or threat of force or violence and/or by putting the victim in fear. Data Elements and Sub-Elements:
Data Element 1 (ORI) (mandatory):
9-character ORI code
Data Element 2 (Incident Number) (mandatory):
Up to 12-character incident number
Data Element 2A (Cargo Theft) (mandatory):
Y = Yes
N = No
Data Element 3 (Incident Date) (mandatory):
YYYYMMDD
Data Element 4 (Cleared Exceptionally) (mandatory if cleared):
Same as Burglary to Commercial Buildings (220)
Data Element 5 (Exceptional Clearance Date) (conditional, if cleared exceptionally):
YYYYMMDD
Data Element 6 (UCR Offense Code) (mandatory):
120 = Robbery
Data Element 7 (Offense Attempted/Completed) (mandatory):
A = Attempted
C = Completed
Data Element 8 (Offender Suspected of Using) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 8A (Bias Motivation) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 9 (Location Type) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 12 (Type Criminal Activity/Gang Information) (mandatory, up to three):
Same as Burglary to Commercial Buildings (220)
Data Element 13 (Type Weapon/Force Involved) (mandatory):
11 = Firearm (Unspecified)
12 = Handgun
13 = Rifle
14 = Shotgun
15 = Other Firearm
20 = Knife/Cutting Instrument
30 = Blunt Object
35 = Motor Vehicle/Vessel
40 = Personal Weapons (Hands, Feet, Teeth, Etc.) 50 = Poison
60 = Explosives
65 = Fire/Incendiary Device
70 = Drugs/Narcotics/Sleeping Pills
85 = Asphyxiation
90 = Other
95 = Unknown
99 = None
Data Element 14 (Type Property Loss/Etc.) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 15 (Property Description) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 16 (Value of Property) (mandatory):
Numeric value in whole dollars
Data Element 17 (Date Recovered) (conditional, if property recovered):
YYYYMMDD
Data Element 23 (Victim Sequence Number) (mandatory):
001-999 (unique number for each victim)
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
120 = Robbery
Data Element 25 (Type of Victim) (mandatory):
I = Individual
B = Business
F = Financial Institution
G = Government
R = Religious Organization
S = Society/Public
O = Other
U = Unknown
Data Element 26 (Age of Victim) (mandatory, if individual victim):
00 = Unknown
01-98 = Years Old
99 = Over 98 Years Old
NN = Under 24 Hours (Neonate)
NB = 1-6 Days Old (Newborn)
BB = 7-364 Days Old (Baby)
Data Element 27 (Sex of Victim) (mandatory, if individual victim):
M = Male
F = Female
U = Unknown
Data Element 28 (Race of Victim) (mandatory, if individual victim):
W = White
B = Black or African American
I = American Indian or Alaska Native
A = Asian
P = Native Hawaiian or Other Pacific Islander
U = Unknown
Data Element 29 (Ethnicity of Victim) (optional, if individual victim):
H = Hispanic or Latino
N = Not Hispanic or Latino
U = Unknown
Data Element 30 (Resident Status of Victim) (optional, if individual victim):
R = Resident
N = Nonresident
U = Unknown
Data Element 33 (Type Injury) (mandatory, if individual victim):
N = None
B = Apparent Broken Bones
I = Possible Internal Injury
L = Severe Laceration
M = Apparent Minor Injury
O = Other Major Injury
T = Loss of Teeth
U = Unconsciousness
Data Element 34 (Offender Number to be Related) (mandatory, if individual victim):
00 = Unknown
01-99 = Offender Sequence Number
Data Element 35 (Relationship of Victim to Offender) (mandatory, for each offender in Data Element 34, if individual victim):
SE = Spouse
CS = Common-Law Spouse
PA = Parent
SB = Sibling
CH = Child
GP = Grandparent
GC = Grandchild
IL = In-Law
SP = Stepparent
SC = Stepchild
SS = Stepsibling
OF = Other Family Member
AQ = Acquaintance
FR = Friend
NE = Neighbor
BE = Babysittee (Baby)
BG = Boyfriend/Girlfriend
CF = Child of Boyfriend/Girlfriend
XS = Ex-Spouse
EE = Employee
ER = Employer
OK = Otherwise Known
RU = Relationship Unknown
ST = Stranger
VO = Victim Was Offender
XR = Ex-Relationship
Data Element 36 (Offender Sequence Number) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 37 (Age of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 38 (Sex of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39 (Race of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39A (Ethnicity of Offender) (optional):
Same as Burglary to Commercial Buildings (220)
II. Crimes Against Persons
These offenses involve individual victims and are counted as one offense per victim. A. Sex Offenses
Rape (11A)
Definition: The penetration, no matter how slight, of the vagina or anus with any body part or object, or oral penetration by a sex organ of another person, without the consent of the victim. Data Elements and Sub-Elements:
Data Element 1 (ORI) (mandatory):
9-character ORI code
Data Element 2 (Incident Number) (mandatory):
Up to 12-character incident number
Data Element 2A (Cargo Theft) (mandatory):
Y = Yes
N = No
Data Element 3 (Incident Date) (mandatory):
YYYYMMDD
Data Element 4 (Cleared Exceptionally) (mandatory if cleared):
Same as Burglary to Commercial Buildings (220)
Data Element 5 (Exceptional Clearance Date) (conditional, if cleared exceptionally):
YYYYMMDD
Data Element 6 (UCR Offense Code) (mandatory):
11A = Rape
Data Element 7 (Offense Attempted/Completed) (mandatory):
A = Attempted
C = Completed
Data Element 8 (Offender Suspected of Using) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 8A (Bias Motivation) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 9 (Location Type) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 12 (Type Criminal Activity/Gang Information) (mandatory, up to three):
Same as Burglary to Commercial Buildings (220)
Data Element 13 (Type Weapon/Force Involved) (mandatory):
Same as Robbery (120)
Data Element 23 (Victim Sequence Number) (mandatory):
001-999
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11A = Rape
Data Element 25 (Type of Victim) (mandatory):
I = Individual
S = Society/Public
Data Element 25A (Type of Officer Activity/Circumstance) (conditional, if victim is a law enforcement officer):
01 = Responding to Disturbance Call
02 = Burglary in Progress/Pursuing Burglary Suspect
03 = Robbery in Progress/Pursuing Robbery Suspect
04 = Attempting Other Arrest
05 = Civil Disorder
06 = Handling/Transporting/Custody of Prisoner
07 = Investigating Suspicious Person/Circumstance
08 = Ambush-No Warning
09 = Mentally Deranged Assailant
10 = Traffic Pursuit/Stop
11 = All Other
Data Element 25B (Officer Assignment Type) (conditional, if victim is a law enforcement officer):
F = Two-Officer Vehicle
G = One-Officer Vehicle (Alone)
H = One-Officer Vehicle (Assisted)
I = Detective or Special Assignment (Alone)
J = Detective or Special Assignment (Assisted)
K = Other (Alone)
L = Other (Assisted)
Data Element 25C (Officer - ORI Other Jurisdiction) (conditional, if victim is a law enforcement officer from another jurisdiction):
9-character ORI code
Data Element 26 (Age of Victim) (mandatory):
Same as Robbery (120)
Data Element 27 (Sex of Victim) (mandatory):
Same as Robbery (120)
Data Element 28 (Race of Victim) (mandatory):
Same as Robbery (120)
Data Element 29 (Ethnicity of Victim) (optional):
Same as Robbery (120)
Data Element 30 (Resident Status of Victim) (optional):
Same as Robbery (120)
Data Element 33 (Type Injury) (mandatory):
Same as Robbery (120)
Data Element 34 (Offender Number to be Related) (mandatory):
Same as Robbery (120)
Data Element 35 (Relationship of Victim to Offender) (mandatory, for each offender in Data Element 34):
Same as Robbery (120)
Data Element 36 (Offender Sequence Number) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 37 (Age of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 38 (Sex of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39 (Race of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39A (Ethnicity of Offender) (optional):
Same as Burglary to Commercial Buildings (220)
Sodomy (11B)
Definition: Oral or anal sexual intercourse with another person, without the consent of the victim, including cases where the victim is incapable of giving consent because of his/her age or because of his/her temporary or permanent mental or physical incapacity.

Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
11B = Sodomy
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11B = Sodomy
Sexual Assault With An Object (11C)
Definition: The use of an object or instrument to unlawfully penetrate, however slightly, the genital or anal opening of the body of another person, without the consent of the victim, including cases where the victim is incapable of giving consent because of his/her age or because of his/her temporary or permanent mental or physical incapacity. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
11C = Sexual Assault With An Object
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11C = Sexual Assault With An Object
Fondling (11D)
Definition: The touching of the private body parts of another person for the purpose of sexual gratification, without the consent of the victim, including cases where the victim is incapable of giving consent because of his/her age or because of his/her temporary or permanent mental or physical incapacity. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
11D = Fondling
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11D = Fondling
Incest (36A)
Definition: Nonforcible sexual intercourse between persons who are related to each other within the degrees wherein marriage is prohibited by law. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
36A = Incest
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
36A = Incest
Statutory Rape (36B)
Definition: Nonforcible sexual intercourse with a person who is under the statutory age of consent. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
36B = Statutory Rape
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
36B = Statutory Rape
Notes
Clarification on Burglary of a Motor Vehicle: The NIBRS manual classifies break-ins to motor vehicles as Theft From Motor Vehicle (23F) under Larceny/Theft Offenses, not as burglary, because motor vehicles (unless permanently fixed as a residence or office) do not meet the NIBRS definition of a "structure" for burglary. If the intent was to refer to actual burglary of a motor vehicle used as a permanent dwelling, it would fall under Burglary (220) with appropriate location and property codes. Mandatory vs. Conditional vs. Optional Data Elements: Mandatory elements are required for valid data submission. Conditional elements depend on circumstances (e.g., property recovery, law enforcement officer victim). Optional elements are at the agency’s discretion. Dropdown Menus: The numbered lists for each data element’s sub-elements are designed for direct implementation into dropdown menus for standardized data entry systems. Date Format: All date fields (e.g., Incident Date, Exceptional Clearance Date, Date Recovered) must be in YYYYMMDD format. Numeric Fields: Fields like Number of Premises Entered, Number of Stolen/Recovered Motor Vehicles, and Value of Property require numeric inputs in whole numbers. Victim Data for Property Crimes: Most property crimes (except Robbery) do not require victim data unless an individual is directly affected (e.g., a business or society as a victim). Robbery includes victim data due to its violent nature. Weekly Reporting: The listed elements and sub-elements cover all required data for weekly NIBRS reporting, ensuring comprehensive and standardized data collection for the specified crimes. Outline of Specified NIBRS Crimes, Elements, and Sub-Elements
I. Crimes Against Property
A. Burglary/Breaking and Entering
1. Burglary to Commercial Buildings (220)
Definition: The unlawful entry into a commercial building or other structure (e.g., office, store, warehouse) with the intent to commit a felony or a theft. Data Elements and Sub-Elements:
Data Element 1 (ORI) (mandatory):
9-character ORI code
Data Element 2 (Incident Number) (mandatory):
Up to 12-character incident number
Data Element 2A (Cargo Theft) (mandatory):
Y = Yes
N = No
Data Element 3 (Incident Date) (mandatory):
YYYYMMDD (Year, Month, Day)
Data Element 4 (Cleared Exceptionally) (mandatory if cleared):
A = Death of Offender
B = Prosecution Declined
C = In Custody of Other Jurisdiction
D = Victim Refused to Cooperate
E = Juvenile/No Custody
N = Not Applicable
Data Element 5 (Exceptional Clearance Date) (conditional, if cleared exceptionally):
YYYYMMDD
Data Element 6 (UCR Offense Code) (mandatory):
220 = Burglary/Breaking and Entering
Data Element 7 (Offense Attempted/Completed) (mandatory):
A = Attempted
C = Completed
Data Element 8 (Offender Suspected of Using) (mandatory):
A = Alcohol
C = Computer Equipment (Handheld Devices)
D = Drugs/Narcotics
N = Not Applicable
Data Element 8A (Bias Motivation) (mandatory):
11 = Anti-White
12 = Anti-Black or African American
13 = Anti-American Indian or Alaska Native
14 = Anti-Asian
15 = Anti-Native Hawaiian or Other Pacific Islander
16 = Anti-Multiple Races, Group
21 = Anti-Arab
22 = Anti-Hispanic or Latino
23 = Anti-Other Race/Ethnicity/Ancestry
31 = Anti-Jewish
32 = Anti-Catholic
33 = Anti-Protestant
34 = Anti-Islamic (Muslim)
35 = Anti-Other Religion
36 = Anti-Multi-Religious Group
37 = Anti-Atheist/Agnostic
38 = Anti-Mormon
39 = Anti-Jehovah’s Witness
41 = Anti-Eastern Orthodox
42 = Anti-Other Christian
43 = Anti-Buddhist
44 = Anti-Hindu
45 = Anti-Sikh
51 = Anti-Gay (Male)
52 = Anti-Lesbian
53 = Anti-Lesbian, Gay, Bisexual, or Transgender (Mixed Group)
54 = Anti-Transgender
55 = Anti-Gender Non-Conforming
61 = Anti-Physical Disability
62 = Anti-Mental Disability
71 = Anti-Male
72 = Anti-Female
88 = None (No Bias)
99 = Unknown (Bias Unknown)
Data Element 9 (Location Type) (mandatory):
01 = Air/Bus/Train Terminal
02 = Bank/Savings and Loan
03 = Bar/Nightclub
04 = Church/Synagogue/Temple/Mosque
05 = Commercial/Office Building
06 = Construction Site
07 = Convenience Store
08 = Department/Discount Store
09 = Drug Store/Doctor’s Office/Hospital
10 = Field/Woods
11 = Government/Public Building
12 = Grocery/Supermarket
13 = Highway/Road/Alley/Street/Sidewalk
14 = Hotel/Motel/Etc. 15 = Jail/Prison/Penitentiary/Corrections Facility
16 = Lake/Waterway/Beach
17 = Liquor Store
18 = Parking Lot/Garage/Drop Lot
19 = Rental Storage Facility
20 = Residence/Home
21 = Restaurant
22 = School/College
23 = Service/Gas Station
24 = Specialty Store
25 = Other/Unknown
37 = Abandoned/Condemned Structure
38 = Amusement Park
39 = Arena/Stadium/Fairgrounds/Coliseum
40 = ATM Separate from Bank
41 = Auto Dealership New/Used
42 = Camp/Campground
44 = Daycare Facility
45 = Dock/Wharf/Freight/Modal Terminal
46 = Farm Facility
47 = Gambling Facility/Casino/Race Track
48 = Industrial Site
49 = Military Installation
50 = Park/Playground
51 = Rest Area
52 = School-College/University
53 = School-Elementary/Secondary
54 = Shelter-Mission/Homeless
55 = Shopping Mall
56 = Tribal Lands
57 = Community Center
58 = Cyberspace
Data Element 10 (Number of Premises Entered) (mandatory):
01-99
Data Element 11 (Method of Entry) (mandatory):
F = Forced Entry
N = No Forced Entry
Data Element 12 (Type Criminal Activity/Gang Information) (mandatory, up to three):
B = Buying/Receiving
C = Cultivating/Manufacturing/Publishing
D = Distributing/Selling
E = Exploiting Children
J = Juvenile Gang
O = Operating/Promoting/Assisting
P = Possessing/Concealing
T = Transporting/Transmitting/Importing
U = Using/Consuming
G = Other Gang
N = None/Unknown
Data Element 14 (Type Property Loss/Etc.) (mandatory):
1 = None
2 = Burned
3 = Counterfeited/Forged
4 = Damaged/Destroyed
5 = Recovered
6 = Seized
7 = Stolen/Etc. 8 = Unknown
Data Element 15 (Property Description) (mandatory):
01 = Aircraft
02 = Alcohol
03 = Automobile
04 = Bicycle
05 = Bus
06 = Clothes/Furs
07 = Computer Hardware/Software
08 = Consumable Goods
09 = Credit/Debit Cards
10 = Drugs/Narcotics
11 = Drug/Narcotic Equipment
12 = Farm Equipment
13 = Firearms
14 = Gambling Equipment
15 = Heavy Construction/Industrial Equipment
16 = Household Goods
17 = Jewelry/Precious Metals/Gems
18 = Livestock
19 = Merchandise
20 = Money
21 = Negotiable Instruments
22 = Non-Negotiable Instruments
23 = Office-Type Equipment
24 = Other Motor Vehicles
25 = Purses/Handbags/Wallets
26 = Radios/TVs/VCRs/DVD Players
27 = Recordings-Audio/Video
28 = Recreational Vehicles
29 = Structures-Single Occupancy Dwellings
30 = Structures-Other Dwellings
31 = Structures-Other Commercial/Business
32 = Structures-Industrial/Manufacturing
33 = Structures-Public/Community
34 = Structures-Storage
35 = Structures-Other
36 = Tools
37 = Trucks
38 = Vehicle Parts/Accessories
39 = Watercraft
41 = Aircraft Parts/Accessories
42 = Artistic Supplies/Accessories
43 = Building Materials
44 = Camping/Hunting/Fishing Equipment/Supplies
45 = Chemicals
46 = Collections/Collectibles
47 = Crops
48 = Documents/Personal or Business
49 = Explosives
59 = Firearm Accessories
60 = Fuel
61 = Identity Documents
62 = Identity-Intangible
64 = Law Enforcement Equipment
65 = Lawn/Yard/Garden Equipment
66 = Logging Equipment
67 = Medical/Medical Lab Equipment
68 = Metals, Non-Precious
69 = Musical Instruments
70 = Pets
71 = Photographic/Optical Equipment
72 = Portable Electronic Communications
73 = Recreational/Sports Equipment
74 = Scrap Metal
75 = Tobacco
76 = Trailers
77 = Watercraft Equipment/Parts/Accessories
78 = Weapons-Other
88 = Pending Inventory (Unknown)
99 = Other
Data Element 16 (Value of Property) (mandatory):
Numeric value in whole dollars
Data Element 17 (Date Recovered) (conditional, if property recovered):
YYYYMMDD
Data Element 36 (Offender Sequence Number) (mandatory):
00 = Unknown
01-99 = Offender Sequence Number
Data Element 37 (Age of Offender) (mandatory):
00 = Unknown
01-98 = Years Old
99 = Over 98 Years Old
Data Element 38 (Sex of Offender) (mandatory):
M = Male
F = Female
U = Unknown
Data Element 39 (Race of Offender) (mandatory):
W = White
B = Black or African American
I = American Indian or Alaska Native
A = Asian
P = Native Hawaiian or Other Pacific Islander
U = Unknown
Data Element 39A (Ethnicity of Offender) (optional):
H = Hispanic or Latino
N = Not Hispanic or Latino
U = Unknown
2. Burglary to Residential Structures (220)
Definition: The unlawful entry into a residential structure (e.g., house, apartment, condominium) with the intent to commit a felony or a theft. Data Elements and Sub-Elements:
Identical to Burglary to Commercial Buildings (220), except the Data Element 9 (Location Type) will typically be:
20 = Residence/Home
29 = Structures-Single Occupancy Dwellings (in Data Element 15, if applicable)
30 = Structures-Other Dwellings (in Data Element 15, if applicable)
B. Larceny/Theft Offenses
1. Theft From Motor Vehicle (23F)
Definition: The unlawful taking of property from within a motor vehicle, not constituting burglary. Data Elements and Sub-Elements:
Same as Burglary to Commercial Buildings (220), except:
Data Element 6 (UCR Offense Code) (mandatory):
23F = Theft From Motor Vehicle
Data Element 10 (Number of Premises Entered): Not applicable
Data Element 11 (Method of Entry): Not applicable
C. Motor Vehicle Theft
1. Motor Vehicle Theft (240)
Definition: The theft or attempted theft of a motor vehicle. Data Elements and Sub-Elements:
Same as Burglary to Commercial Buildings (220), except:
Data Element 6 (UCR Offense Code) (mandatory):
240 = Motor Vehicle Theft
Data Element 10 (Number of Premises Entered): Not applicable
Data Element 11 (Method of Entry): Not applicable
Data Element 18 (Number of Stolen Motor Vehicles) (mandatory):
00-99
Data Element 19 (Number of Recovered Motor Vehicles) (conditional, if recovered):
00-99
D. Robbery
1. Robbery (120)
Definition: The taking or attempting to take anything of value from the care, custody, or control of a person or persons by force or threat of force or violence and/or by putting the victim in fear. Data Elements and Sub-Elements:
Data Element 1 (ORI) (mandatory):
9-character ORI code
Data Element 2 (Incident Number) (mandatory):
Up to 12-character incident number
Data Element 2A (Cargo Theft) (mandatory):
Y = Yes
N = No
Data Element 3 (Incident Date) (mandatory):
YYYYMMDD
Data Element 4 (Cleared Exceptionally) (mandatory if cleared):
Same as Burglary to Commercial Buildings (220)
Data Element 5 (Exceptional Clearance Date) (conditional, if cleared exceptionally):
YYYYMMDD
Data Element 6 (UCR Offense Code) (mandatory):
120 = Robbery
Data Element 7 (Offense Attempted/Completed) (mandatory):
A = Attempted
C = Completed
Data Element 8 (Offender Suspected of Using) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 8A (Bias Motivation) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 9 (Location Type) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 12 (Type Criminal Activity/Gang Information) (mandatory, up to three):
Same as Burglary to Commercial Buildings (220)
Data Element 13 (Type Weapon/Force Involved) (mandatory):
11 = Firearm (Unspecified)
12 = Handgun
13 = Rifle
14 = Shotgun
15 = Other Firearm
20 = Knife/Cutting Instrument
30 = Blunt Object
35 = Motor Vehicle/Vessel
40 = Personal Weapons (Hands, Feet, Teeth, Etc.) 50 = Poison
60 = Explosives
65 = Fire/Incendiary Device
70 = Drugs/Narcotics/Sleeping Pills
85 = Asphyxiation
90 = Other
95 = Unknown
99 = None
Data Element 14 (Type Property Loss/Etc.) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 15 (Property Description) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 16 (Value of Property) (mandatory):
Numeric value in whole dollars
Data Element 17 (Date Recovered) (conditional, if property recovered):
YYYYMMDD
Data Element 23 (Victim Sequence Number) (mandatory):
001-999 (unique number for each victim)
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
120 = Robbery
Data Element 25 (Type of Victim) (mandatory):
I = Individual
B = Business
F = Financial Institution
G = Government
R = Religious Organization
S = Society/Public
O = Other
U = Unknown
Data Element 26 (Age of Victim) (mandatory, if individual victim):
00 = Unknown
01-98 = Years Old
99 = Over 98 Years Old
NN = Under 24 Hours (Neonate)
NB = 1-6 Days Old (Newborn)
BB = 7-364 Days Old (Baby)
Data Element 27 (Sex of Victim) (mandatory, if individual victim):
M = Male
F = Female
U = Unknown
Data Element 28 (Race of Victim) (mandatory, if individual victim):
W = White
B = Black or African American
I = American Indian or Alaska Native
A = Asian
P = Native Hawaiian or Other Pacific Islander
U = Unknown
Data Element 29 (Ethnicity of Victim) (optional, if individual victim):
H = Hispanic or Latino
N = Not Hispanic or Latino
U = Unknown
Data Element 30 (Resident Status of Victim) (optional, if individual victim):
R = Resident
N = Nonresident
U = Unknown
Data Element 33 (Type Injury) (mandatory, if individual victim):
N = None
B = Apparent Broken Bones
I = Possible Internal Injury
L = Severe Laceration
M = Apparent Minor Injury
O = Other Major Injury
T = Loss of Teeth
U = Unconsciousness
Data Element 34 (Offender Number to be Related) (mandatory, if individual victim):
00 = Unknown
01-99 = Offender Sequence Number
Data Element 35 (Relationship of Victim to Offender) (mandatory, for each offender in Data Element 34, if individual victim):
SE = Spouse
CS = Common-Law Spouse
PA = Parent
SB = Sibling
CH = Child
GP = Grandparent
GC = Grandchild
IL = In-Law
SP = Stepparent
SC = Stepchild
SS = Stepsibling
OF = Other Family Member
AQ = Acquaintance
FR = Friend
NE = Neighbor
BE = Babysittee (Baby)
BG = Boyfriend/Girlfriend
CF = Child of Boyfriend/Girlfriend
XS = Ex-Spouse
EE = Employee
ER = Employer
OK = Otherwise Known
RU = Relationship Unknown
ST = Stranger
VO = Victim Was Offender
XR = Ex-Relationship
Data Element 36 (Offender Sequence Number) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 37 (Age of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 38 (Sex of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39 (Race of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39A (Ethnicity of Offender) (optional):
Same as Burglary to Commercial Buildings (220)
II. Crimes Against Persons
A. Sex Offenses
1. Rape (11A)
Definition: The penetration, no matter how slight, of the vagina or anus with any body part or object, or oral penetration by a sex organ of another person, without the consent of the victim. Data Elements and Sub-Elements:
Data Element 1 (ORI) (mandatory):
9-character ORI code
Data Element 2 (Incident Number) (mandatory):
Up to 12-character incident number
Data Element 2A (Cargo Theft) (mandatory):
Y = Yes
N = No
Data Element 3 (Incident Date) (mandatory):
YYYYMMDD
Data Element 4 (Cleared Exceptionally) (mandatory if cleared):
Same as Burglary to Commercial Buildings (220)
Data Element 5 (Exceptional Clearance Date) (conditional, if cleared exceptionally):
YYYYMMDD
Data Element 6 (UCR Offense Code) (mandatory):
11A = Rape
Data Element 7 (Offense Attempted/Completed) (mandatory):
A = Attempted
C = Completed
Data Element 8 (Offender Suspected of Using) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 8A (Bias Motivation) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 9 (Location Type) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 12 (Type Criminal Activity/Gang Information) (mandatory, up to three):
Same as Burglary to Commercial Buildings (220)
Data Element 13 (Type Weapon/Force Involved) (mandatory):
Same as Robbery (120)
Data Element 23 (Victim Sequence Number) (mandatory):
001-999
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11A = Rape
Data Element 25 (Type of Victim) (mandatory):
I = Individual
S = Society/Public
Data Element 25A (Type of Officer Activity/Circumstance) (conditional, if victim is a law enforcement officer):
01 = Responding to Disturbance Call
02 = Burglary in Progress/Pursuing Burglary Suspect
03 = Robbery in Progress/Pursuing Robbery Suspect
04 = Attempting Other Arrest
05 = Civil Disorder
06 = Handling/Transporting/Custody of Prisoner
07 = Investigating Suspicious Person/Circumstance
08 = Ambush-No Warning
09 = Mentally Deranged Assailant
10 = Traffic Pursuit/Stop
11 = All Other
Data Element 25B (Officer Assignment Type) (conditional, if victim is a law enforcement officer):
F = Two-Officer Vehicle
G = One-Officer Vehicle (Alone)
H = One-Officer Vehicle (Assisted)
I = Detective or Special Assignment (Alone)
J = Detective or Special Assignment (Assisted)
K = Other (Alone)
L = Other (Assisted)
Data Element 25C (Officer - ORI Other Jurisdiction) (conditional, if victim is a law enforcement officer from another jurisdiction):
9-character ORI code
Data Element 26 (Age of Victim) (mandatory):
Same as Robbery (120)
Data Element 27 (Sex of Victim) (mandatory):
Same as Robbery (120)
Data Element 28 (Race of Victim) (mandatory):
Same as Robbery (120)
Data Element 29 (Ethnicity of Victim) (optional):
Same as Robbery (120)
Data Element 30 (Resident Status of Victim) (optional):
Same as Robbery (120)
Data Element 33 (Type Injury) (mandatory):
Same as Robbery (120)
Data Element 34 (Offender Number to be Related) (mandatory):
Same as Robbery (120)
Data Element 35 (Relationship of Victim to Offender) (mandatory, for each offender in Data Element 34):
Same as Robbery (120)
Data Element 36 (Offender Sequence Number) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 37 (Age of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 38 (Sex of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39 (Race of Offender) (mandatory):
Same as Burglary to Commercial Buildings (220)
Data Element 39A (Ethnicity of Offender) (optional):
Same as Burglary to Commercial Buildings (220)
2. Sodomy (11B)
Definition: Oral or anal sexual intercourse with another person, without the consent of the victim, including cases where the victim is incapable of giving consent because of his/her age or because of his/her temporary or permanent mental or physical incapacity. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
11B = Sodomy
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11B = Sodomy
3. Sexual Assault With An Object (11C)
Definition: The use of an object or instrument to unlawfully penetrate, however slightly, the genital or anal opening of the body of another person, without the consent of the victim, including cases where the victim is incapable of giving consent because of his/her age or because of his/her temporary or permanent mental or physical incapacity. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
11C = Sexual Assault With An Object
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11C = Sexual Assault With An Object
4. Fondling (11D)
Definition: The touching of the private body parts of another person for the purpose of sexual gratification, without the consent of the victim, including cases where the victim is incapable of giving consent because of his/her age or because of his/her temporary or permanent mental or physical incapacity. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
11D = Fondling
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
11D = Fondling
5. Incest (36A)
Definition: Nonforcible sexual intercourse between persons who are related to each other within the degrees wherein marriage is prohibited by law. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
36A = Incest
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
36A = Incest
6. Statutory Rape (36B)
Definition: Nonforcible sexual intercourse with a person who is under the statutory age of consent. Data Elements and Sub-Elements:
Same as Rape (11A), except:
Data Element 6 (UCR Offense Code) (mandatory):
36B = Statutory Rape
Data Element 24 (Victim Connected to UCR Offense Code) (mandatory):
36B = Statutory Rape
Notes
Clarification on Burglary of a Motor Vehicle: The NIBRS manual classifies break-ins to motor vehicles as Theft From Motor Vehicle (23F) under Larceny/Theft Offenses, not as burglary, because motor vehicles (unless permanently fixed as a residence or office) do not meet the NIBRS definition of a "structure" for burglary. If the intent was to refer to actual burglary of a motor vehicle used as a permanent dwelling, it would fall under Burglary (220) with appropriate location and property codes. Mandatory vs. Conditional vs. Optional Data Elements: Mandatory elements are required for valid data submission. Conditional elements depend on circumstances (e.g., property recovery, law enforcement officer victim). Optional elements are at the agency’s discretion. Dropdown Menus: The numbered lists for each data element’s sub-elements are designed for direct implementation into dropdown menus for standardized data entry systems. Date Format: All date fields (e.g., Incident Date, Exceptional Clearance Date, Date Recovered) must be in YYYYMMDD format. Numeric Fields: Fields like Number of Premises Entered, Number of Stolen/Recovered Motor Vehicles, and Value of Property require numeric inputs in whole numbers. Victim Data for Property Crimes: Most property crimes (except Robbery) do not require victim data unless an individual is directly affected (e.g., a business or society as a victim). Robbery includes victim data due to its violent nature. Weekly Reporting: The listed elements and sub-elements cover all required data for weekly NIBRS reporting, ensuring comprehensive and standardized data collection for the specified crimes.

