import sqlite3
import time
import progressbar
import collections

# Useful containers
airport = collections.namedtuple('airport', 'id altitude magvar')
runway = collections.namedtuple('runway', 'id hgd_t length_ft type')

# Progress bar basic design
widgets = [' [', progressbar.Timer(), '] ',
           progressbar.Bar(marker='=', left='[', right=']')]

conn = None

def setupDatabase():
    FSXpath = _findFSXpath()
    xml_file = FSXpath + r'\runways.xml'
    apt = _parseXMLfile(xml_file)

    rebuild_db = True
    global conn
    print(conn)
    conn = _buildDatabase(rebuild_db)
    print(conn)
    _insertDatabaseData(conn, apt)

def findFSXpath():
    import winreg

    win_fsx_key = r'SOFTWARE\WOW6432Node\Microsoft\microsoft games\flight simulator\10.0'
    Key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, win_fsx_key)
    FSXpath = winreg.QueryValueEx(Key, "SetupPath")[0]

    return FSXpath


def parseXMLfile(xml_file):
    import xml.etree.ElementTree as ET

    data_node = ET.parse(xml_file)
    apt_list = data_node.getroot()
    # Airport data is stored in list apt:
    # apt[0]: airport data (namedtuple airport)
    # apt[1]: list[namedtuple runway]
    apt = []

    bar = progressbar.ProgressBar(widgets=widgets,
                                  max_value=len(apt_list))
    i = 0
    bar.start()
    for a in apt_list:
        bar.update(i)
        i = i + 1
        apt_rwy = []
        apt_icao = a.get('id')
        apt_alt = float(a.find('Altitude').text)
        apt_magvar = float(a.find('MagVar').text)
        apt_data = airport(apt_icao, apt_alt, apt_magvar)
        for rwy in a.iter('Runway'):
            rwy_id = rwy.get('id')
            rwy_hdg_m = float(rwy.find('Hdg').text)
            rwy_hdg_t = rwy_hdg_m + apt_magvar
            rwy_len_ft = float(rwy.find('Len').text)
            rwy_type = rwy.find('Def').text
            rwy_data = runway(rwy_id, rwy_hdg_t, rwy_len_ft, rwy_type)
            apt_rwy.append(rwy_data)
        apt.append([apt_data, apt_rwy])
    bar.finish()

    return apt


def buildDatabase(is_new=False):
    import sys
    global conn
    if 'airports' in sys.modules:
        sql_file = r'.\airports\airports.db'
    else:
            sql_file = r'.\airports.db'
    conn = sqlite3.connect(sql_file)

    if is_new:
        n_commands = 4
        sql = [None] * n_commands
        sql[0] = '''drop table if exists FSXairport;'''
        sql[1] = '''drop table if exists FSXrunway;'''
        sql[2] = ('''create table FSXairport (icao char(4), altitude float, '''
                 '''magvar float);''')
        sql[3] = ('''create table FSXrunway (id text(3), hdg_t float, '''
                 '''length_ft float, surface_type text, airportID integer, '''
                 '''foreign key (airportID) references FSXairport(rowid));''')
        for i in range(n_commands):
            conn.execute(sql[i])
        conn.commit()

        fout = open( 'db_structure.sql', 'w' )
        for cmd in sql:
            fout.write( cmd+'\n' )
        fout.close()

    return conn


def insertDatabaseData(conn, apt):
    c = conn.cursor()
    for a in apt:
        data = a[0]
        rwys = a[1]
        # Inserting the airport..
        cmd = 'insert into FSXairport values ' + str(tuple(data)) + ';'
        c.execute(cmd)
        last_id = c.lastrowid        
        # and its runways. The airportid comes from c.lastrowid
        for r in rwys:
            cmd = 'insert into FSXrunway values ' + str(tuple(r)+(last_id,)) + ';'
            c.execute(cmd)

    conn.commit()

def extractAirportData(icao):
    apt, rwy = extractDBAirportData(icao)

    return airport(*apt), [runway(*r) for r in rwy]

def extractDBAirportData(icao):
    ''' Usage:
        apt, rwys = extractAirportData('KBOS')

        apt is an airport structure ('airport', 'id altitude magvar')
        rwys is a list of runway structure ('runway', 'id hgd_t length_ft type')

        NB. Airport icao MUST be capitalzed.
    '''
    global conn
    c = conn.cursor()
    cmd = '''select * from FSXairport where icao=?'''
    c.execute(cmd, (icao, ))
    apt_data = c.fetchone()
    
    cmd = '''select rowid from FSXairport where icao=?'''
    c.execute(cmd, (icao, ))
    airportid = c.fetchone()[0]

    apt_rwy = []
    cmd = '''select * from FSXrunway where airportid=?'''
    for r in c.execute(cmd, (airportid, )):
        apt_rwy.append(r[:-1])
    
    return (apt_data, apt_rwy)
    

if __name__ == '__main__':
''' Testing the code '''
    FSXpath = findFSXpath()
    xml_file = FSXpath + r'\runways.xml'
    # xml_file = r'.\runways.xml'
    apt = parseXMLfile(xml_file)

    rebuild_db = True
    conn = buildDatabase(rebuild_db)

    insertDatabaseData(conn, apt)

    apt, rwys = extractAirportData('KBOS')
    print(apt)
    for r in rwys:
        print(r)

    conn.close()

