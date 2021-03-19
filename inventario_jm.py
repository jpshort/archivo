import csv
import odoorpc
from datetime import datetime,date

db        = 'ortec'
user      = 'admin'
password  = 'admin'
odoo = odoorpc.ODOO('207.246.65.71',port=80)
print(odoo.db.list())


# Login
#odoo.login('db_name', 'user', 'passwd')
odoo.login(db, user, password)


def get_product_id(codigo,auxilar):

    datos = odoo.execute('product.product', 'search_read', [('default_code', '=', codigo)],
                         ['id', 'uom_id','type'])
    if codigo == "-":
        datos = odoo.execute('product.product', 'search_read', [('name', '=', auxilar)],
                             ['id', 'uom_id','type'])
    producto = []
    for c in datos:
        producto.append(c['id'])
        producto.append(c['uom_id'][0])
        producto.append(c['type'])
        #print(c['id'])
        return producto

    return False

Stock_line = odoo.env['stock.inventory.line']
def create_inventory_line(producto,index,cantidad):
    #print('product'," ",producto[2])
    datos = odoo.execute('stock.inventory.line', 'search_read', [('company_id','=',1),
                                                                 ('product_id', '=',producto[2]),
                                                                 ('inventory_id', '=', producto[0])],
                         ['product_id'])

    for c in datos:
        ff = c['product_id']
        print("Existe en inventario ",ff," ", producto[2]," linea",index," Cant. ",producto[4])
        return ff
    #try:
    #print(producto[0],' Location ',producto[1])
    line = Stock_line.create({'inventory_id':producto[0],
                              'location_id': producto[1],
                              'inventory_location_id':producto[1],
                              'product_id' : producto[2],
                              'product_uom_id':producto[3],
                              'product_qty':producto[4],
                              'company_id':1})
    #except:
     #   print("Error","   " , index," Cantidad ",cantidad," ",producto[2])


Stock = odoo.env['stock.inventory']
def create_inventory(product):
    now =  datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")

    line = Stock.create({'name': product[0],
                         'location_id': product[1],
                         'date': dt_string,
                         'filter':'partial',
                         'state':'confirm',
                         'company_id': "1"})

    return line

def get_location(name):
    Locations = odoo.env['stock.location']
    full_name = "Physical Locations/{name}".format(name = name)
    #print("full "," ",full_name)
    location = Locations.search([('complete_name','=',full_name)]) #'Physical Locations/AP/Existencia'
    #print(location)
    for c in Locations.browse(location):
        #print(c.complete_name)
        return c.id

def exists_stock(location_id):
    Stocks = odoo.env['stock.inventory']
    stock = Stocks.search( [('company_id','=',1),('location_id', '=',location_id),('state','=','confirm')])

    for c in Stocks.browse(stock):
        return True

    return False

def get_stock_id(location_id):
    invent = []
    datos  = odoo.execute('stock.inventory', 'search_read', [('company_id','=',1),('location_id', '=',location_id),('state','=','confirm')],
                              ['id', 'location_id'])

    for c in datos:
        invent.append(c['id'])
        invent.append(c['location_id'][0])
        return invent

def data_file(file_name):
    linea = []
    invent = []
    with open(file_name, newline='') as f:  # , encoding='utf-8'
        reader = csv.reader(f)
        i = 0
        c = 0
        n = 0
        for row in reader:
            i += 1
            if i == 1:
                continue

            linea = []
            invent = []
            #if i > 3:
             #   break

            # Buscar el ID de la ubicacion por medio del nombre

            location = get_location(row[3])
            codigo = row[0]
            nombre = row[2]
            print(i," ",location,"  fuera ",row[3])
            #break
            #Buscar si el producto existe
            product = get_product_id(codigo, nombre)

            description =  "Registro Inventario Inicial  {date}, {location}".format(date = date.today(), location = row[3])
            inventory_id = [description, location]

            if not row[4]:
                continue

            if float(row[4].replace(',', '').replace('RD$', '')) == 0:
                continue

            try:
                cantidad = float(row[4].replace(',', '').replace('RD$', ''))
            except:
                pass

            if exists_stock(location):
                invent = get_stock_id(location)
            else:
                stock_id = create_inventory(inventory_id)
                invent.append(stock_id)
                invent.append(location)
            #print(invent[0],' location oooo ',invent[1])
            linea.append(invent[0])
            linea.append(invent[1])

            if product:
                linea.append(product[0])
                linea.append(product[1])
                linea.append(cantidad)
                print(i," ",product[0])
                if product[2] != 'product':
                    continue
                    # print(i," producto ",product[2])
                # print(" INVENTARIO  ",i, cantidad, " ", row[0])
                create_inventory_line(linea, row[1], cantidad)

    """
    location = get_location('AM/BAN-2.4-10')
    product = ['Registro Inventario Inicial 15/01/2021 AM/BAN-2.4-10', location]
    stock_id = 0
    if not exists_stock(location):
        stock_id = create_inventory(product)

    print(stock_id)
    """

data_file('existenciaporubicacionof12345.csv')
##data_file('inventario_ubicacion.csv')

#get_location('AP/Existencia')