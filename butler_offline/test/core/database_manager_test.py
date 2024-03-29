from butler_offline.core import database_manager
from butler_offline.core.database_manager import MultiPartCsvReader
from butler_offline.core.database_manager import DatabaseParser
from butler_offline.core import file_system
from butler_offline.test.core.file_system_stub import FileSystemStub


def mock_filesystem():
    file_system.INSTANCE = FileSystemStub()


def write_db_file_stub(name, stub):
    file_system.instance().write('./Database_' + name + '.csv', stub)


def test_database_path_from():
    assert database_manager.database_path_from('TestUser') == './Database_TestUser.csv'


def teste_read_with_full_database():
    mock_filesystem()
    write_db_file_stub('testuser', FULL_DB)

    database = database_manager.read('testuser', set())

    assert database.name == 'testuser'
    assert len(database.einzelbuchungen.content) == 25
    assert len(database.einzelbuchungen.content[database.einzelbuchungen.content.Dynamisch == False]) == 2
    assert database.einzelbuchungen.select().sum() == -675

    assert len(database.dauerauftraege.content) == 2
    assert database.dauerauftraege.content.Kategorie.tolist() == ['Essen', 'Miete']

    assert len(database.depotwerte.content) == 1
    assert len(database.order.content) == 3
    assert len(database.depotauszuege.content) == 1
    assert len(database.orderdauerauftrag.content) == 1


def teste_write_with_full_database():
    mock_filesystem()
    write_db_file_stub('testuser', FULL_DB)

    database = database_manager.read('testuser', set())
    database_manager.write(database)

    assert file_system.instance().read('./Database_testuser.csv') == file_system.instance().stub_pad_content(FULL_DB)


def teste_write_with_old_database_should_migrate():
    mock_filesystem()
    write_db_file_stub('testuser', FULL_DB_OLD)

    database = database_manager.read('testuser', set())
    database_manager.write(database)

    assert file_system.instance().read('./Database_testuser.csv') == file_system.instance().stub_pad_content(FULL_DB)


FULL_DB_OLD = '''Datum,Kategorie,Name,Wert,Tags
2017-10-10,Essen,Essen gehen,-10.0,[]
2017-11-11,Essen,Nochwas,-1.0,[]

 Dauerauftraege 
Endedatum,Kategorie,Name,Rhythmus,Startdatum,Wert
2017-09-18,Essen,Other Something,monatlich,2017-01-12,-1.0
2017-09-30,Miete,Miete,monatlich,2017-01-13,-1.0

 Gemeinsame Buchungen 
Datum,Kategorie,Name,Wert,Person
2017-12-30,Miete,monatlich,-200.0,TestUser
2017-12-31,Miete,monatlich,-200.0,Partner
 Sparbuchungen 
Datum,Name,Wert,Typ,Konto
2017-12-31,Beispielsparen,100,manueller Auftrag,Beispielkonto
 Depotwerte 
Name,ISIN
1depotwert,1isin
 Order
Datum,Name,Konto,Depotwert,Wert
2020-02-02,1order,1konto,1depotwert,200
 Dauerauftr_Ordr 
Startdatum,Endedatum,Rhythmus,Name,Konto,Depotwert,Wert
2020-01-1,2020-02-02,monatlich,dauerauftrag_order,1konto,1depotwert,123
 Depotauszuege
Datum,Depotwert,Konto,Wert
2020-01-01,1depotwert,1konto,111

stechzeiten...
'''

FULL_DB = '''Datum,Kategorie,Name,Wert,Tags
2017-10-10,Essen,Essen gehen,-10.0,[]
2017-11-11,Essen,Nochwas,-1.0,[]

 Dauerauftraege 
Endedatum,Kategorie,Name,Rhythmus,Startdatum,Wert
2017-09-18,Essen,Other Something,monatlich,2017-01-12,-1.0
2017-09-30,Miete,Miete,monatlich,2017-01-13,-1.0

 Gemeinsame Buchungen 
Datum,Kategorie,Name,Wert,Person
2017-12-30,Miete,monatlich,-200.0,TestUser
2017-12-31,Miete,monatlich,-200.0,Partner

 Sparbuchungen 
Datum,Name,Wert,Typ,Konto
2017-12-31,Beispielsparen,100.0,manueller Auftrag,Beispielkonto

 Sparkontos 
Kontoname,Kontotyp

 Depotwerte 
Name,ISIN,Typ
1depotwert,1isin,ETF

 Order 
Datum,Name,Konto,Depotwert,Wert
2020-02-02,1order,1konto,1depotwert,200.0

 Dauerauftr_Ordr 
Startdatum,Endedatum,Rhythmus,Name,Konto,Depotwert,Wert
2020-01-01,2020-02-02,monatlich,dauerauftrag_order,1konto,1depotwert,123.0

 Depotauszuege 
Datum,Depotwert,Konto,Wert
2020-01-01,1depotwert,1konto,111.0
'''


def test_read_multipart_csv_reader():
    test_content = [
        '1,2', '2,3', '3,4',
        'B', '3,4', '4,5'
    ]

    reader = MultiPartCsvReader({'A', 'B', 'C'}, 'A')
    reader.from_string(test_content)

    assert reader.get_string('A') == '1,2\n2,3\n3,4'
    assert reader.get_string('B') == '3,4\n4,5'
    assert reader.get_string('C') == ''


def test_read_database_parser():
    database_parser = DatabaseParser()

    database_parser.from_string(full_db_parser)

    assert database_parser.einzelbuchungen() == einzelbuchungen
    assert database_parser.dauerauftraege() == dauerauftraege
    assert database_parser.gemeinsame_buchungen() == gemeinsame_buchungen


einzelbuchungen = '''Datum,Kategorie,Name,Wert,Tags
2017-10-10,Essen,Essen gehen,-10.0,[]
2017-11-11,Essen,Nochwas,-1.0,[]'''


dauerauftraege = '''Endedatum,Kategorie,Name,Rhythmus,Startdatum,Wert
2017-09-18,Essen,Other Something,monatlich,2017-01-12,-1.0
2017-09-30,Miete,Miete,monatlich,2017-01-13,-1.0'''


gemeinsame_buchungen = '''Datum,Kategorie,Name,Wert,Person
2017-12-30,Miete,monatlich,-200.0,TestUser
2017-12-31,Miete,monatlich,-200.0,Partner'''


full_db_parser = '''
{einzelbuchungen}
Dauerauftraege
{dauerauftraege}
Gemeinsame Buchungen
{gemeinsame_buchungen}
'''.format(einzelbuchungen=einzelbuchungen, dauerauftraege=dauerauftraege, gemeinsame_buchungen=gemeinsame_buchungen)\
    .split('\n')
