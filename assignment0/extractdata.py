import pypdf
from pypdf import PdfReader
import re
from io import BytesIO

def extractdata(pdf_file):
    '''Extracts raw data from pdf file and processes the raw data to extract relavant information'''
    reader = PdfReader(pdf_file)
    num_pages = len(reader.pages)
    raw_incidents_text = list()
    for page_number in range(num_pages):
        page = reader.pages[page_number]
        text = page.extract_text()
        raw_incidents_text.append(text)
    print("EXTRACTED ALL INCIDENTS TEXT!!\n")
    all_incidents = process_incidents_by_page(raw_incidents_text)
    return all_incidents

def process_incidents_by_page(raw_incidents_text:list):
    '''Processes the whole incidents data page-by-page, then line-by-line in each page 
        to extract relavant keys and values'''
    final_incidents_list = list()
    count = 0
    for page_text in raw_incidents_text:
        incidents_by_page = page_text.split('\n')
        for incident_string in incidents_by_page:
            count+=1
            incident_time, incident_ori, incident_number = None, None, None
            incident_address, incident_nature = None, None
            incident_time = extract_time(incident_string)
            if not incident_time:
                continue
            incident_number = extract_number(incident_string)
            if not incident_number:
                continue
            incident_address, last_index = extract_address(incident_string)
            if not incident_address:
                continue
            incident_nature, incident_ori = extract_nature_and_ori(incident_string, last_index)
            if not incident_ori or incident_nature is None:
                continue
            final_incidents_list.append((incident_time, incident_number, incident_address, incident_nature, incident_ori))
    print('PROCESSED ALL INCIDENTS!!')
    print('Total rows count in extracted incidents list = ', count)
    print('Total actual incidents count = ', len(final_incidents_list))
    return final_incidents_list

def extract_nature_and_ori(input_string, start_index):
    '''Parses the nature of the incident and the ori number from the raw incident string'''
    standard_oris = ['OK0140200', 'EMSSTAT', '14005']
    ori_match = re.search(r'(\w+)$', input_string)
    ori_number = None
    incident_nature = None
    end_index = -1
    if ori_match:
        for s in standard_oris:
            if s in ori_match.group(1):
                ori_number = s
                end_index = input_string.find(ori_number)
                break
    if not ori_number:
        return None, None
    incident_nature = input_string[start_index+1:end_index].strip(' ')
    return incident_nature, ori_number

def extract_address(input_string):
    '''Parses the location of the incident from the raw incident string'''
    street_type_list = [
        'Allee', 'Alley', 'Ally', 'Aly', 'Anex', 'Annex',
        'Annx', 'Anx', 'Arc', 'Arcade', 'Av', 'Ave',
        'Aven', 'Avenu', 'Avenue', 'Avn', 'Avnue', 'Bayoo',
        'Bayou', 'Bch', 'Beach', 'Bend', 'Bg', 'Bgs',
        'Blf', 'Blfs', 'Bluf', 'Bluff', 'Bluffs', 'Blvd',
        'Bnd', 'Bot', 'Bottm', 'Bottom', 'Boul', 'Boulevard',
        'Boulv', 'Br', 'Branch', 'Brdge', 'Brg', 'Bridge',
        'Brk', 'Brks', 'Brnch', 'Broadway', 'Brook', 'Brooks',
        'Btm', 'Burg', 'Burgs', 'Byp', 'Bypa', 'Bypas',
        'Bypass', 'Byps', 'Byu', 'Camp', 'Canyn', 'Canyon',
        'Cape', 'Causeway', 'Causwa', 'Cen', 'Cent', 'Center',
        'Centers', 'Centr', 'Centre', 'Cir', 'Circ', 'Circl',
        'Circle', 'Circles', 'Cirs', 'Clb', 'Clf', 'Clfs',
        'Cliff', 'Cliffs', 'Club', 'Cmn', 'Cmns', 'Cmp',
        'Cnter', 'Cntr', 'Cnyn', 'Common', 'Commons', 'Cor',
        'Corner', 'Corners', 'Cors', 'Course', 'Court', 'Courts',
        'Cove', 'Coves', 'Cp', 'Cpe', 'Crcl', 'Crcle',
        'Creek', 'Cres', 'Crescent', 'Crest', 'Crk', 'Crossing',
        'Crossroad', 'Crossroads', 'Crse', 'Crsent', 'Crsnt', 'Crssng',
        'Crst', 'Cswy', 'Ct', 'Ctr', 'Ctrs', 'Cts',
        'Curv', 'Curve', 'Cv', 'Cvs', 'Cyn', 'Dale',
        'Dam', 'Div', 'Divide', 'Dl', 'Dm', 'Dr',
        'Driv', 'Drive', 'Drives', 'Drs', 'Drv', 'Dv',
        'Dvd', 'Est', 'Estate', 'Estates', 'Ests', 'Exp',
        'Expr', 'Express', 'Expressway', 'Expw', 'Expy', 'Ext',
        'Extension', 'Extensions', 'Extn', 'Extnsn', 'Exts', 'Fall',
        'Falls', 'Ferry', 'Field', 'Fields', 'Flat', 'Flats',
        'Fld', 'Flds', 'Fls', 'Flt', 'Flts', 'Ford',
        'Fords', 'Forest', 'Forests', 'Forg', 'Forge', 'Forges',
        'Fork', 'Forks', 'Fort', 'Frd', 'Frds', 'Freeway',
        'Freewy', 'Frg', 'Frgs', 'Frk', 'Frks', 'Frry',
        'Frst', 'Frt', 'Frway', 'Frwy', 'Fry', 'Ft',
        'Fwy', 'Garden', 'Gardens', 'Gardn', 'Gateway', 'Gatewy',
        'Gatway', 'Gdn', 'Gdns', 'Glen', 'Glens', 'Gln',
        'Glns', 'Grden', 'Grdn', 'Grdns', 'Green', 'Greens',
        'Grn', 'Grns', 'Grov', 'Grove', 'Groves', 'Grv',
        'Grvs', 'Gtway', 'Gtwy', 'Harb', 'Harbor', 'Harbors',
        'Harbr', 'Haven', 'Hbr', 'Hbrs', 'Heights', 'Highway',
        'Highwy', 'Hill', 'Hills', 'Hiway', 'Hiwy', 'Hl',
        'Hllw', 'Hls', 'Hollow', 'Hollows', 'Holw', 'Holws',
        'Hrbor', 'Ht', 'Hts', 'Hvn', 'Hway', 'Hwy',
        'Inlet', 'Inlt', 'Is', 'Island', 'Islands', 'Isle',
        'Isles', 'Islnd', 'Islnds', 'Iss', 'Jct', 'Jction',
        'Jctn', 'Jctns', 'Jcts', 'Junction', 'Junctions', 'Junctn',
        'Juncton', 'Key', 'Keys', 'Knl', 'Knls', 'Knol',
        'Knoll', 'Knolls', 'Ky', 'Kys', 'Lake', 'Lakes',
        'Land', 'Landing', 'Lane', 'Lck', 'Lcks', 'Ldg',
        'Ldge', 'Lf', 'Lgt', 'Lgts', 'Light', 'Lights',
        'Lk', 'Lks', 'Ln', 'Lndg', 'Lndng', 'Loaf',
        'Lock', 'Locks', 'Lodg', 'Lodge', 'Loop', 'Loops',
        'Lp', 'Mall', 'Manor', 'Manors', 'Mdw', 'Mdws',
        'Meadow', 'Meadows', 'Medows', 'Mews', 'Mill', 'Mills',
        'Mission', 'Missn', 'Ml', 'Mls', 'Mnr', 'Mnrs',
        'Mnt', 'Mntain', 'Mntn', 'Mntns', 'Motorway', 'Mount',
        'Mountain', 'Mountains', 'Mountin', 'Msn', 'Mssn', 'Mt',
        'Mtin', 'Mtn', 'Mtns', 'Mtwy', 'Nck', 'Neck',
        'Opas', 'Orch', 'Orchard', 'Orchrd', 'Oval', 'Overpass',
        'Ovl', 'Park', 'Parks', 'Parkway', 'Parkways', 'Parkwy',
        'Pass', 'Passage', 'Path', 'Paths', 'Pike', 'Pikes',
        'Pine', 'Pines', 'Pkway', 'Pkwy', 'Pkwys', 'Pky',
        'Pl', 'Place', 'Plain', 'Plains', 'Plaza', 'Pln',
        'Plns', 'Plz', 'Plza', 'Pne', 'Pnes', 'Point',
        'Points', 'Port', 'Ports', 'Pr', 'Prairie', 'Prk',
        'Prr', 'Prt', 'Prts', 'Psge', 'Pt', 'Pts',
        'Rad', 'Radial', 'Radiel', 'Radl', 'Ramp', 'Ranch',
        'Ranches', 'Rapid', 'Rapids', 'Rd', 'Rdg', 'Rdge',
        'Rdgs', 'Rds', 'Rest', 'Ridge', 'Ridges', 'Riv',
        'River', 'Rivr', 'Rnch', 'Rnchs', 'Road', 'Roads',
        'Route', 'Row', 'Rpd', 'Rpds', 'Rst', 'Rte',
        'Rue', 'Run', 'Rvr', 'Shl', 'Shls', 'Shoal',
        'Shoals', 'Shoar', 'Shoars', 'Shore', 'Shores', 'Shr',
        'Shrs', 'Skwy', 'Skyway', 'Smt', 'Spg', 'Spgs',
        'Spng', 'Spngs', 'Spring', 'Springs', 'Sprng', 'Sprngs',
        'Spur', 'Spurs', 'Sq', 'Sqr', 'Sqre', 'Sqrs',
        'Sqs', 'Squ', 'Square', 'Squares', 'St', 'Sta',
        'Station', 'Statn', 'Stn', 'Str', 'Stra', 'Strav',
        'Straven', 'Stravenue', 'Stravn', 'Stream', 'Street', 'Streets',
        'Streme', 'Strm', 'Strt', 'Strvn', 'Strvnue', 'Sts',
        'Sumit', 'Sumitt', 'Summit', 'Ter', 'Terr', 'Terrace',
        'Throughway', 'Tpke', 'Trace', 'Traces', 'Track', 'Tracks',
        'Trafficway', 'Trail', 'Trailer', 'Trails', 'Trak', 'Trce',
        'Trfy', 'Trk', 'Trks', 'Trl', 'Trlr', 'Trlrs',
        'Trls', 'Trnpk', 'Trwy', 'Tunel', 'Tunl', 'Tunls',
        'Tunnel', 'Tunnels', 'Tunnl', 'Turnpike', 'Turnpk', 'Un',
        'Underpass', 'Union', 'Unions', 'Uns', 'Upas', 'Valley',
        'Valleys', 'Vally', 'Vdct', 'Via', 'Viadct', 'Viaduct',
        'View', 'Views', 'Vill', 'Villag', 'Village', 'Villages',
        'Ville', 'Villg', 'Villiage', 'Vis', 'Vist', 'Vista',
        'Vl', 'Vlg', 'Vlgs', 'Vlly', 'Vly', 'Vlys',
        'Vst', 'Vsta', 'Vw', 'Vws', 'Walk', 'Walks',
        'Wall', 'Way', 'Ways', 'Well', 'Wells', 'Wl',
        'Wls', 'Wy', 'Xing', 'Xrd', 'Xrds']
    street_type_pattern = r'\b(?:' + '|'.join(map(re.escape, street_type_list)) + r')\b'
    start_pattern = r'\d{4}-\d{8}'
    start_match = re.search(start_pattern, input_string)
    street_address = None
    last_index = -1
    if start_match:
        start_index = start_match.end()
        matches = list(re.finditer(rf'({street_type_pattern})', input_string[start_index:], flags=re.IGNORECASE))
        if matches:
            #finding the longest matched street address
            longest_match = max(matches, key=lambda m: m.end() - start_index)
            # Extract the substring from the starting pattern until the longest matched street type
            street_address = input_string[start_index:start_index + longest_match.start() + len(longest_match.group(1))].strip()
            last_index = longest_match.end() + start_index - 1
    return street_address, last_index
    
    

def extract_number(input_string):
    '''Parses the incident number from the raw incident string'''
    incident_number_pattern = re.compile(r'(\d{4}-\d{8}\s)')
    match = re.search(incident_number_pattern, input_string)
    if match:
        incident_number = match.group(1).strip(' ')
    else:
        incident_number = None
    return incident_number

def extract_time(input_string):
    '''Parses the time when incident occurred from the raw incident string'''
    time_pattern = re.compile(r'\b(\d{1,2}:\d{2})\b')
    match = re.search(time_pattern, input_string)
    if match:
        incident_time = match.group(1)
    else:
        incident_time = None
    return incident_time