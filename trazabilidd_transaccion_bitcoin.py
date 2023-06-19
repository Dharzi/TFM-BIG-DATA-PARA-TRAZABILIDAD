"""
Realiza la trazabilidad de una transaccion

FUNCIONES:
"""
import json,sys,os
import numpy as np
import bitcoinlib as bilib
import re
import warnings

# Filtrar advertencias específicas
#####warnings.filterwarnings("ignore", category=DeprecationWarning, module="transaction_deserialize")
#####warnings.filterwarnings("ignore", category=DeprecationWarning)

##import warnings warnings.filterwarnings("ignore", category=DeprecationWarning)
#with warnings.catch_warnings():
warnings.simplefilter("ignore")

def descargar_bloque(ablock_height):
    """
    Descarga de Bitcoin Core, el bloque y sus transacciones en dos ficheros json, 
    uno para el nodo y otro para todas sus transacciones 

    Argumentos:
        block_height -- Altura del bloque a descargar

    Devuelve:
        Nombre fichero bloque descargado
        Nombre fichero con las transacciones del bloque
    """
    from bitcoinrpc.authproxy import AuthServiceProxy
    #from bitcoinlib.services.bitcoind import BitcoindClient
    
    # Configura la conexión RPC con Bitcoin Core
    rpc_user = 'usuariorcp'
    rpc_password = 'RcpT7m8l0ck'
    rpc_port = 8332
    rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@localhost:{rpc_port}", timeout=60)
    
    # Establece la altura del bloque deseado
    #block_height = 791163
    block_height = int(sys.argv[1])
    path_bitcoin_cli = '/Blockchain/bitcoin-22.0/bin/'
    
    # Obtiene el hash del bloque deseado
    block_hash = rpc_connection.getblockhash(block_height)
    # Obtiene los detalles del bloque deseado
    
    try:
        block_data = rpc_connection.getblock(block_hash)
    except:
        print("Bloque no disponible, no se puede continuar")
    
    # Nombre del archivo donde se guardarán los datos de las transacciones
    file_name_bloque = '/Blockchain/codigo/json/bloque_'+str(block_height)+'.json'
    print('Descargando la estructura del bloque: '+str(block_height)+' en el fichero: '+file_name_bloque)
    # Obtiene los detalles del bloque
    with open(file_name_bloque, 'w') as file:
        # Guarda los datos de la transacción en el archivo en formato json
        block_data_json = json.dumps(block_data, defaactual=str)
        file.write(json.dumps(block_data_json, indent=4))
        file.write('\n')
    # Obtiene los hashes de las transacciones contenidas en el bloque
    transaction_hashes = block_data['tx']
    # Nombre del archivo donde se guardarán los datos de las transacciones
    file_name_transacciones = '/Blockchain/codigo/json/transacciones_bloque_'+block_height+'.json'
    print('Descargando las transacciones del bloque: '+block_height+' en el fichero: '+file_name_bloque)
    # Itera sobre cada hash de transacción y utiliza el comando `getrawtransaction` para obtener los datos de la transacción
    with open(file_name_transacciones, 'w') as file:
        #for tx_hash in block_data['tx']:
        for tx_hash in transaction_hashes:
            # Obtiene los detalles de cada transacción
            tx_data = rpc_connection.getrawtransaction(tx_hash, True, block_hash)
        
            # Guarda los datos de la transacción en el archivo en formato json
            transaction_data = json.dumps(tx_data, defaactual=str)
            file.write(json.dumps(transaction_data, indent=4))
            file.write('\n')

    return(file_name_bloque, file_name_transacciones)
    
def descarga_transacciones_fichero(fichero):
    """
    Lee el fichero con las transsacciones de un bloque en formato json y las descarga 
    devolviendo un array numpy de diccionarios siendo cada diccionario una transacción

    Argumentos:
        fichero -- Fichero a descargar con su path completo
               Ej: /Blockchain/codigo/json/transacciones_bloque_792726.json

    Devuelve:
        Array numpy de diccionarios siendo cada diccionario una transacción
    """
    
    #Crea diccionario donde almacenar la lectura del fichero json
    transactions_dict=dict()

    numLinea = int(0)
  
    # Abrir el archivo JSON
    #with open('/Blockchain/codigo/json/transacciones_bloque_792726_792728.json') as f:
    with open(fichero, 'r') as f: 
        for linea in f:
            numLinea += 1
            # Cargar los datos del archivo en un string
            transactions = json.loads(linea)
            
            #Carga la transaccion en formato string en un diccionario
            transactions_dict = json.loads(transactions)

            #Esta transaccion de dicciorio la agrega a un array de numpy
            if (numLinea == 1):
                #Crea el array al leer la primera linea del fichero
                transactions_array_dict = np.array(transactions_dict)
            else:
                #Añade el diccionario al array
                transactions_array_dict = np.append(transactions_array_dict, transactions_dict)
           
    return(transactions_array_dict)

def decodifica_transaction(transaccion):
    """
    Decodifica la transaccion pasada como parámetro devolviendo los datos de la misma

    Argumento:
       Transaccion completa a decodificar en formato diccionario 
    
    Devuelve:
    """
    from io import StringIO

    tx = bilib.transactions.transaction_deserialize(transaccion['hex'],network='bitcoin', check_size=True)
    decoded_transaction = {
        'version': tx.version,
        'lock_time': tx.locktime,
        'inputs': [],
        'outputs': []
    }

    #Prepara buffer para guardar la salida por pantalla del comando tx.info() en una variable
    buffer = StringIO()
    sys.stdout = buffer

    print(tx.info())
    decoded_transaction = buffer.getvalue()

    # restore stdout to defaactual for print()
    sys.stdout = sys.__stdout__
  
    return decoded_transaction


def buscar_transaccion_en_archivo(archivo, address_buscado):
    """
    Busca el address pasado como parámetro en el fichero json indicado dentro de la session vout
    Si la encuentra devuelve el numero de la linea de fichero donde esta la transaccion
    sino devuelve 0

    Argumento:
       Archivo donde busca la transacion
       Identificado de la transaccion a buscar
    
    Devuelve:
       Numero de linea del archivo donde está la transaccion
    """
    with open(archivo, 'r') as file:
        for linea_num, linea in enumerate(file, 1):
            try:
                json_data = json.loads(linea)
                if buscar_address_en_json(json_data, address_buscado):
                    return linea_num
            except json.JSONDecodeError:
                continue
    return None

def buscar_address_en_json(json_data, address_buscado):
    """
    Busca dentro de la seccion vin del json, el txid de la transaccion pasada como parámetro 
    Si la encuentra devuelve true sino false

    Argumento:
       json done buscar
       txid de la transaccion a buscar
    
    Devuelve:
       true si lo encuentra sino false
    """
    json_data_dict=json.loads(json_data)
    if isinstance(json_data_dict, dict):
        if "vout" in json_data_dict:
            for vout_item in json_data_dict["vout"]:
                if isinstance(vout_item, dict) and "scriptPubKey" in vout_item:
                    try:
                        if vout_item["scriptPubKey"]["address"] == address_buscado:
                            return True
                    except:
                        continue
    elif isinstance(json_data_dict, list):
        for item in json_data_dict:
            if buscar_address_en_json(item, txid_buscado):
                return True
    return False

def generar_nombre_wallet():
    import random
    import string

    """
    Genera un nombre aleatorio alfanumerico dde 8 digitos 

    Argumento:
    
    Devuelve:
       string de 8 digitos
    """
    caracteres = string.ascii_letters + string.digits
    referencia = ''.join(random.choices(caracteres, k=8))
    return referencia

def crear_wallet(wallet_id, address, amount,transac_rec,transac_env,btc_env,btc_rec,bal_act,wallet_id_ant):
    """
    Crea wallet

    Argumento:
        wallet_id  - Identificador de wallet 
        address    - Direccion del input de la transaccion
        amount     - Cantidad en btc del imput de la transaccion
        transac_rec - Tranferencia recibida
        transac_env - Tranferencia enviada
        btc_env    - Bitcoin enviado
        btc_rec    - Bitcoin recibido
        bal_act    - Balance actual
        Wallet_id_ant - Identificador del wallet al que apunta este wallet. Si tiene None es que no apunta a ninguno
    
    Devuelve:
       wallet
    """
    
    wallet = {
        "wallet_id": wallet_id,
        "direcciones": [
            {"address": address  , 
              "amount": amount},
            ],
        "transferencias_recibidas": transac_rec,
        "transferencias_enviadas": transac_env,
        "btc_enviado": btc_env,
        "btc_recibido": btc_rec,
        "balance_actual": bal_act,
        "wallet_id_ant": wallet_id_ant
        }
    
    return wallet

def buscar_wallet_id(wallets, address_a_buscar):
    """
    Busca el identificador del wallet en el array se wallets que tenga internamente la direccion 
    pasada como parametro

    Argumento:
        wallets - array de wallets 
        address - Direccion a buscar en los wallet
   
    Devuelve:
       wallet_id, si no lo encuentra devuelve None
    """
    
    #Tamanno array wallets
    tam_array_wallets = wallets.shape[0]
    contador=1 #Se inicializa a 1 porque el primer elemento del array esta vacio

    while contador < tam_array_wallets:
        wallet = wallets[contador] 
        direcciones = wallet.get("direcciones", [])
        for direccion in direcciones:
            if direccion.get("address") == address_a_buscar:
                return wallet.get("wallet_id")  
        contador+=1
    
    return None
                

########################
### Codigo principal ###
########################

#Ficheros con bloques descargados a tratar
fichero1 = '/Blockchain/codigo/json/transacciones_bloque_1_792726.json'
fichero2 = '/Blockchain/codigo/json/transacciones_bloque_2_792727.json'
fichero3 = '/Blockchain/codigo/json/transacciones_bloque_3_792728.json'


#########################################################################
#### Descarga el fichero json con el bloque de transaccione a tratar ####
#### Lo decodifica metiendo el resultado en un array numpy           ####
#########################################################################

#Descarga el fichero json con las transacciones del bloque actual
transacion_array_dictactual = descarga_transacciones_fichero(fichero3)

# Obtener el tamaño del array
tam_array_dictactual = transacion_array_dictactual.shape[0]
num_linea_array = 0

#Trata cada una de las trnsacciones del bloque actual y crea tantos wallets como sean necesarios
#con los input de cada transaccion, para esste estuio solo usa ls transacciones que tengan un 
#input y como maximo 2 ouput
while num_linea_array < tam_array_dictactual:

    transaccion_dictactual = transacion_array_dictactual[num_linea_array] # Fichero 
    
    #Decodidfica la actualima transaccion
    decode_transactionactual = decodifica_transaction(transaccion_dictactual)

    # Extrae información utilizando expresiones regulares
    tractual_transaction_id = re.search(r"Transaction (.+)", decode_transactionactual).group(1)
    tractual_network = re.search(r"Network: (.+)", decode_transactionactual).group(1)
    tractual_version = re.search(r"Version: (\d+)", decode_transactionactual).group(1)
    tractual_witness_type = re.search(r"Witness type: (.+)", decode_transactionactual).group(1)
    tractual_status = re.search(r"Status: (.+)", decode_transactionactual).group(1)
    tractual_verified = re.search(r"Verified: (\w+)", decode_transactionactual).group(1)
    
    #Genera diccionarios para imputs con direccion y cantidad de bitcoin y lo mismo con los outputs
    # Extrae el contenido de la sección de Inputs
    tractual_inputs_section = re.search(r"Inputs\n(.+?)Outputs", decode_transactionactual, re.DOTALL).group(1)
    
    # Utiliza expresiones regulares para extraer los datos de cada input y almacenarlos en un diccionario
    tractual_inputs = re.findall(r"- (.+?) (\d+\.\d+) BTC (.+?) (.+?)$", tractual_inputs_section, re.MULTILINE)
    
    # Construye un diccionario con los datos de los inputs
    tractual_inputs_dict = {}
    address_actual=''
    for input in tractual_inputs:
        address_actual = input[0] #Almaceno la direccion para obtener la cantidad total
        amount =  input[1]
        type_  =  input[2]
        tractual_inputs_dict[address_actual] = {
            "amount": amount
        }
    
    #Genera diccionarios para imputs con direccion y cantidad de bitcoin y lo mismo con los outputs
    #Extrae el contenido de la sección de Outputs
    tractual_outputs_section = re.search(r"Outputs\n(.+?)Size", decode_transactionactual, re.DOTALL).group(1)
    
    # Utiliza expresiones regulares para extraer los datos de cada output y almacenarlos en un diccionario
    tractual_outputs = re.findall(r"- (.+?) (\d+\.\d+) BTC (.+?) (.+?)$", tractual_outputs_section, re.MULTILINE)
    
    # Construye un diccionario con los datos de los outputs
    tractual_outputs_dict = {}
    for output in tractual_outputs:
        address = output[0]
        amount = output[1]
        type_ = output[2]
        status = output[3]
        tractual_outputs_dict[address] = {
            "amount": amount,
            "type": type_,
            "status": status
        }
    
    tractual_size = re.search(r"Size: (\d+)", decode_transactionactual).group(1)
    tractual_vsize = re.search(r"Vsize: (\d+)", decode_transactionactual).group(1)
    tractual_fee = re.search(r"Fee: (.+)", decode_transactionactual).group(1)
    tractual_confirmations = re.search(r"Confirmations: (.+)", decode_transactionactual).group(1)
    tractual_block = re.search(r"Block: (.+)", decode_transactionactual).group(1)
    

    ##########################################################################################################    
    ###Busca el address del input de la transaccion en cada uno de los ficheros con los bloques descargados###
    ##########################################################################################################

    #Busca el address del input de la transaccion dentro de la seccion output de cada uno de los ficheros con 
    #los bloques descargados, si lo encuentra indica el numero de linea del fichero
  
    for fich in (fichero2, fichero1):
        num_linea = buscar_transaccion_en_archivo(fich, address_actual)   

        if num_linea:
            #Descarga el fichero json con las transacciones del bloque actual
            transacion_array_dictant = descarga_transacciones_fichero(fich)

            #Transaccion del bloque anterior
            transaccion_dictant = transacion_array_dictant[num_linea-1] # Resta 1 al numero de linea porque los arrays empiezan por 0

            #Decodidfica la transaccion anterior
            decode_transactionant = decodifica_transaction(transaccion_dictant)
            
            # Extraer información utilizando expresiones regulares
            trans_transaction_id = re.search(r"Transaction (.+)", decode_transactionant).group(1)
            trans_network = re.search(r"Network: (.+)", decode_transactionant).group(1)
            trans_version = re.search(r"Version: (\d+)", decode_transactionant).group(1)
            trans_witness_type = re.search(r"Witness type: (.+)", decode_transactionant).group(1)
            trans_status = re.search(r"Status: (.+)", decode_transactionant).group(1)
            trans_verified = re.search(r"Verified: (\w+)", decode_transactionant).group(1)
            
            #Generar diccionarios para imputs con direccion y cantidad de bitcoin y lo mismo con los outputs
            # Extraer el contenido de la sección de Inputs
            trans_inputs_section = re.search(r"Inputs\n(.+?)Outputs", decode_transactionant, re.DOTALL).group(1)
            
            # Utilizar expresiones regulares para extraer los datos de cada input y almacenarlos en un diccionario
            trans_inputs = re.findall(r"- (.+?) (\d+\.\d+) BTC (.+?) (.+?)$", trans_inputs_section, re.MULTILINE)
            
            # Construir un diccionario con los datos de los inputs
            trans_inputs_dict = {}
            for input in trans_inputs:
                address = input[0]
                amount =  input[1]
                type_  =  input[2]
                trans_inputs_dict[address] = {
                    "amount": amount
                    #"type": type_
                }
            
            #Generar diccionarios para imputs con direccion y cantidad de bitcoin y lo mismo con los outputs
            # Extraer el contenido de la sección de Outputs
            trans_outputs_section = re.search(r"Outputs\n(.+?)Size", decode_transactionant, re.DOTALL).group(1)
            
            # Utilizar expresiones regulares para extraer los datos de cada output y almacenarlos en un diccionario
            trans_outputs = re.findall(r"- (.+?) (\d+\.\d+) BTC (.+?) (.+?)$", trans_outputs_section, re.MULTILINE)
            
            # Construir un diccionario con los datos de los outputs
            trans_outputs_dict = {}
            for output in trans_outputs:
                address = output[0]    
                #trans_amount = float(output[1])
                amount = output[1]
                type_ = output[2]
                status = output[3]
                trans_outputs_dict[address] = {
                    "amount": amount,
                    "type": type_,
                    "status": status
                }
            
            trans_size = re.search(r"Size: (\d+)", decode_transactionant).group(1)
            trans_vsize = re.search(r"Vsize: (\d+)", decode_transactionant).group(1)
            trans_fee = re.search(r"Fee: (.+)", decode_transactionant).group(1)
            trans_confirmations = re.search(r"Confirmations: (.+)", decode_transactionant).group(1)
            trans_block = re.search(r"Block: (.+)", decode_transactionant).group(1)
            
            #Obtiene del bloque anterior la cantidad total del input del bloque actual, 
            #es decir el dinero que se envía, para ello mira del bloque anterior aquel 
            #output cuyo address coincida con el address del bloque anterior
            for output in trans_outputs:
                address_ant = output[0]
                if (address_actual == address_ant):
                    tractual_inputs_dict[address_actual]["amount"] = trans_outputs_dict[address_ant]["amount"] 


            ########################################################################
            ####Creo un array de diccionarios con las transacciones decodificada####
            ####Para este estudio solo usa las transaciones que tengan un input ####
            ####y como máximo 2 output                                          ####
            ########################################################################

            #Creo un diccionario con la transaccion actual decodificada            
            transaction_decodificada = {
                "Transaction_ID": tractual_transaction_id,
                "Network": tractual_network,
                "Version": tractual_version,
                "Witness_Type": tractual_witness_type,
                "Status": tractual_status,
                "Verified": tractual_verified,
                "Inputs": {
                },
                "Outputs": [],  
                "Size": tractual_size,
                "Vsize": tractual_vsize,
                "Fee": tractual_fee,
                "Confirmations": tractual_confirmations,
                "Block": tractual_block
            }

            if (len(tractual_inputs_dict) == 1 and len(tractual_outputs_dict) <= 2):            
                #Agrego los inputs decodificadoas en el diccionario
                for address, data in tractual_inputs_dict.items():
                    transaction_decodificada["Inputs"] = {
                        "Address": address,
                        "Amount": data["amount"]
                    }
    
                #Agrego los outputs decodificadoas en el diccionario
                for address, data in tractual_outputs_dict.items():
                    direccion={
                        "Address": address,
                        "Amount": data["amount"],
                        "Type": data["type"],
                        "Status": data["status"]
                    }
    
                    transaction_decodificada["Outputs"].append(direccion)
  
                #Agrego el diccionario con la transacion decodificada en un array de numpy
                try:
                    # Verificar si el array está definido
                    if isinstance(transaction_decodificada_array, np.ndarray):
                        # El array está definido, realizar append
                        transaction_decodificada_array = np.append(transaction_decodificada_array, transaction_decodificada)
                    else:
                        # El array no está definido, crear nuevo array e insertar elemento
                        transaction_decodificada_array = np.array([transaction_decodificada])
                except NameError:
                    # El array no está definido, crear nuevo array e insertar elemento                    
                    transaction_decodificada_array = np.array([transaction_decodificada])                        
   
                for address, data in tractual_inputs_dict.items():
                    address_wallet = address
                    amount_wallet = data["amount"]
    
                #######################################################################################
                #### Se crea un array de wallets uno para cada input de las transacciones a tratar ####
                #######################################################################################  
                #Crea un wallet con el input de la transacion actual
                wallet_id=generar_nombre_wallet()
                wallet=crear_wallet(wallet_id, address_wallet, amount_wallet, 0, 0, 0, 0, 0,None)
        
                # Agrego el wallet al array numpy de wallets
                try:
                    # Verificar si el array está definido
                    if isinstance(wallets_array, np.ndarray):
                        # El array está definido, realizar append
                        wallets_array = np.append(wallets_array, wallet)
                    else:
                        # El array no está definido, crear nuevo array e insertar elemento
                        wallets_array = np.array([wallet])
                except NameError:
                    # El array no está definido, crear nuevo array e insertar elemento                    
                    wallets_array = np.array([wallet])      
                    
       
                #####################################################
                #### Imprime la informacion de las transacciones ####
                #####################################################
                # Imprimir la información extraída
                print('Imprime la información extraída de la Transaccion del bloque actual')
                print("Transaction ID:", tractual_transaction_id)
                print("Network:", tractual_network)
                print("Version:", tractual_version)
                print("Witness Type:", tractual_witness_type)
                print("Status:", tractual_status)
                print("Verified:", tractual_verified)
                print()
                print("Inputs:")
                
                # Imprimir el diccionario de inputs
                for address, data in tractual_inputs_dict.items():
                    print("Address:", address)
                    print("Amount:", data["amount"]) 
                    print()
                
                print("Outputs:")
                
                # Imprimir el diccionario de outputs
                for address, data in tractual_outputs_dict.items():
                    print("Address:", address)
                    print("Amount:", data["amount"])
                    print("Type:", data["type"])
                    print("Status:", data["status"])
                    print()
                
                print("Size:", tractual_size)
                print("Vsize:", tractual_vsize)
                print("Fee:", tractual_fee)
                print("Confirmations:", tractual_confirmations)
                print("Block:", tractual_block)
                       
                # Imprimir la información extraída del boque anterior
                print()
                print()
                print('Imprime la información extraída de la Transaccion del bloque anterior')
                print("Transaction ID:", trans_transaction_id)
                print("Network:", trans_network)
                print("Version:", trans_version)
                print("Witness Type:", trans_witness_type)
                print("Status:", trans_status)
                print("Verified:", trans_verified)
                print()
                print("Inputs:")
                
                # Imprimir el diccionario de outputs
                for address, data in trans_inputs_dict.items():
                    print("Address:", address)
                    print("Amount:", data["amount"])  
                    print()
                
                print("Outputs:")

                # Imprimir el diccionario de outputs
                for address, data in trans_outputs_dict.items():
                    print("Address:", address)
                    print("Amount:", data["amount"])
                    print("Type:", data["type"])
                    print("Status:", data["status"])
                    print()
                
                print("Size:", trans_size)
                print("Vsize:", trans_vsize)
                print("Fee:", trans_fee)
                print("Confirmations:", trans_confirmations)
                print("Block:", trans_block)

            break 
    num_linea_array+=1

##################################################################
#### Actualiza wallets creados viendo si el address de estos  ####
#### esta en el input y/o el output de la transaccion y con   ####
#### esta informacion actualiza las transacciones enviadas    ####
#### recibidas, bitcoin enviados y recibidos asi como el      ####
#### balance.                                                 ####
##################################################################
tam_array_wallets = wallets_array.shape[0]
cont_wallet=0

while cont_wallet < tam_array_wallets:
    wallet = wallets_array[cont_wallet] # Fichero 

    direcciones = wallet.get("direcciones", [])

    trans_env=0
    trans_reci=0
    btc_env=0
    btc_reci=0
    balance=0
    
    for direccion in direcciones:      
        #Obtiene la direccion de imput
        address_wallet = direccion.get("address") 

        #Por cada direccion se recorre el de las transacciones decodificadas
        tam_trans_decodificada = transaction_decodificada_array.shape[0]
        cont_transac=0

        while cont_transac < tam_trans_decodificada:
            address_en_input = 'N'
            address_en_output = 'N'
            transac_decodif =  transaction_decodificada_array[cont_transac]

            #Recorre la lista de input     
            amount_input_transac='Null'           
            for clave, valor in transac_decodif["Inputs"].items():            
                if (clave == 'Address'):
                    address_input_transac=valor
                elif (clave == 'Amount'):
                    amount_input_transac=valor
                    
                if ((address_wallet == address_input_transac) and (amount_input_transac != 'Null')):
                    trans_env+=1
                    btc_env=amount_input_transac
                    address_en_input = 'Y'
                                                                        
                amount_input_transac='Null'

            #Recorre la lista de output
            amount_output_trans='Null'
            tipo_output_trans='Null'
            output_list=[]
            for output in transac_decodif['Outputs']:
                address_output_trans=output['Address']
                amount_output_trans=output['Amount']
                tipo_output_trans=output['Type']

                if (address_wallet == address_output_trans):
                    trans_reci+=1
                    btc_reci=amount_output_trans
                    address_en_output = 'Y'
                elif (address_wallet != address_output_trans):
                    #Almacena la transaccion en una lista
                    output_list.append([address_output_trans,amount_output_trans,tipo_output_trans])

            #Si la direccion esta en el input 
            if (address_en_input == 'Y' ):
                wallet_id_nuevo=generar_nombre_wallet()
                
                #Obtiene el tipo de address del wallet extrayendo los 4 primeros digitos del mismo
                tipo_address_wallet = address_wallet[:4]

                #Si la lista tiene un solo elemento creo un wallet muevo apuntando al wallet actual
                if (len(output_list)==1):
                    #Crea un wallet con el output de la transacion actual
                    wallet_id_actual=wallet.get("wallet_id")
                    address_output=output_list[0][0]
                    amount_output=output_list[0][1]
                    wallet=crear_wallet(wallet_id_nuevo, address_output, amount_output, 1, 0, 0, amount_output, amount_output,wallet_id_actual)

                    #Añade el diccionario al array
                    wallets_array = np.append(wallets_array, wallet)
                elif (len(output_list) > 1): 
                    #Crea una nueva lista odenada por el amount de menor a mayor
                    output_list_sorted = sorted(output_list, key=lambda x: float(x[1]))

                    address_output_ant = None
                    tipo_address_output_ant = None
                    amount_output_ant = None

                    #Recorre la lista ordenada
                    for i in range(len(output_list_sorted)):
                        address_output = output_list_sorted[i][0]
                        amount_output = output_list_sorted[i][1]

                        #Obtiene el tipo de address del address extrayendo los 4 primeros digitos del mismo
                        tipo_address_output = address_output[:4]

                        if (i == 0): #Guarda los datos de la primera transaccion en variables
                            address_output_ant = address_output
                            tipo_address_output_ant = tipo_address_output
                            amount_output_ant = amount_output

                        elif (i >  0):
                            #Si el address del input esta en los output, con la transaccion que tiene diferente direccion 
                            #crea un wallet nuevo apuntando al wallet actual
                            #Con la otra transaccion lo que hace es incrementar el numero de transacciones recibidas en 1
                            #y el btc_recibido con la cantidad de la transaccion
                            if ( address_en_output == 'Y' ):
                                if ( address_wallet == address_output_ant ):
                                    #Aumenta la transacciones recibidas y los btc_recibidos del wallet que se esta tratando
                                    #con los datos de la transaccion anterior
                                    trans_reci += 1
                                    btc_reci = float(btc_reci) + float(amount_output_ant)

                                    #Crea un wallet con el output de la transacion actual
                                    wallet_id_actual=wallet.get("wallet_id")
                                    wallet=crear_wallet(wallet_id_nuevo, address_output, amount_output, 1, 0, 0, amount_output, amount_output,wallet_id_actual) 
                                    #Añade el diccionario al array
                                    wallets_array = np.append(wallets_array, wallet)

                                else:
                                    #Aumenta la transacciones recibidas y los btc_recibidos del wallet que se esta tratando
                                    #con los datos de la transaccion actual
                                    trans_reci += 1
                                    btc_reci = float(btc_reci) + float(amount_output)

                                    #Crea un wallet con el output de la transacion anterior
                                    wallet_id_actual=wallet.get("wallet_id")
                                    wallet=crear_wallet(wallet_id_nuevo, address_output_ant, amount_output_ant, 1, 0, 0, amount_output_ant, amount_output_ant,wallet_id_actual)  
                                    #Añade el diccionario al array
                                    wallets_array = np.append(wallets_array, wallet)
                            else: #si el address del wallet no coincide con ninguno de los del output
                                #Mira los tipos de address del output
                                #Si ninguno coincide con el tipo de addres de la direccion del wallet o ambos coinciden:
                                #    crea un nuevo wallet usando la transaccion anterior que es la que tiene menor cuantia por lo que se entiende
                                #    que es la que se ha usado para pagar la transaccion
                                #    con la transaccion actual se mete su direccion en el wallet que se esta tratando incrementando 
                                #    el valor de las transcciones recibidas en así como el de los btc_recibidos con el amount de la transaccion
                                #En el caso de que solo coindida uno de los tipos
                                #   crea un nuevo wallet con la transaccion que tiene un tipo diferente
                                #   con la otra mete su direccion en el wallet que se esta tratando incrementando el valor de las transcciones 
                                #   recibidas en así como el de los btc_recibidos con el amount de la transaccion
                                if (( tipo_address_wallet == tipo_address_output and tipo_address_wallet == tipo_address_output_ant) 
                                    or
                                    ( tipo_address_wallet != tipo_address_output and tipo_address_wallet != tipo_address_output_ant) 
                                    ):

                                    #Crea un wallet con el output de la transacion anterior
                                    wallet_id_actual=wallet.get("wallet_id")
                                    wallet=crear_wallet(wallet_id_nuevo, address_output_ant, amount_output_ant, 1, 0, 0, amount_output_ant, amount_output_ant,wallet_id_actual) 
                                    #Añade el diccionario al array
                                    wallets_array = np.append(wallets_array, wallet)

                                    #Agrega la direccion al wallet que se esta tratando
                                    nuevo_address = {'address': address_output, 'amount': amount_output}
                                    # Acceder a la lista de direcciones y agregar el nuevo address
                                    wallets_array[cont_wallet]['direcciones'].append(nuevo_address)

                                    trans_reci += 1                                    
                                    btc_reci = float(btc_reci) + float(amount_output)
                                else:
                                    if (tipo_address_wallet == tipo_address_output ):
                                        #Crea un wallet con el output de la transacion anterior
                                        wallet_id_actual=wallet.get("wallet_id")
                                        wallet=crear_wallet(wallet_id_nuevo, address_output_ant, amount_output_ant, 1, 0, 0, amount_output_ant, amount_output_ant,wallet_id_actual)   
                                        #Añade el diccionario al array
                                        wallets_array = np.append(wallets_array, wallet)
    
                                        #Agrega la direccion al wallet que se esta tratando
                                        nuevo_address = {'address': address_output, 'amount': amount_output}
                                        # Acceder a la lista de direcciones y agregar el nuevo address
                                        wallets_array[cont_wallet]['direcciones'].append(nuevo_address)
    
                                        trans_reci += 1
                                        btc_reci = float(btc_reci) + float(amount_output)

                                    else:
                                        #Crea un wallet con el output de la transacion actual
                                        wallet_id_actual=wallet.get("wallet_id")
                                        wallet=crear_wallet(wallet_id_nuevo, address_output, amount_output, 1, 0, 0, amount_output, amount_output,wallet_id_actual) 
                                        #Añade el diccionario al array
                                        wallets_array = np.append(wallets_array, wallet)
    
                                        #Agrega la direccion al wallet que se esta tratando
                                        nuevo_address = {'address': address_output_ant, 'amount': amount_output_ant}
                                        # Acceder a la lista de direcciones y agregar el nuevo address
                                        wallets_array[cont_wallet]['direcciones'].append(nuevo_address)
    
                                        trans_reci += 1
                                        btc_reci = float(btc_reci) + float(amount_output)

            #Borro la lista
            del output_list[:]
 
            cont_transac+=1   
        #Actualiza los valores de la direccion del wallet            
        balance = round(float(btc_reci)-float(btc_env),8)
        wallets_array[cont_wallet]["transferencias_recibidas"] = trans_reci
        wallets_array[cont_wallet]["transferencias_enviadas"] = trans_env
        wallets_array[cont_wallet]["btc_enviado"] = btc_env
        wallets_array[cont_wallet]["btc_recibido"] = btc_reci
        wallets_array[cont_wallet]["balance_actual"] = balance

        #End ttransaccion decodifiada

    cont_wallet+=1
    #End for direcccion wallet
#End while Wallet
print()
print("WALLETS: ",wallets_array)

##Genera fichero json con el array de wallets generado
# Directorio donde se creará el archivo JSON
directorio = '/Blockchain/codigo/json/'

# Nombre del archivo JSON
nombre_archivo = 'wallets.json'

# Ruta completa del archivo
ruta_archivo = os.path.join(directorio, nombre_archivo)

# Convierte el array NumPy a una lista de Python
lista_wallets = wallets_array.tolist()

# Generar el archivo JSON en el directorio especificado
with open(ruta_archivo, 'w') as file:
    json.dump(lista_wallets, file, indent=4)
