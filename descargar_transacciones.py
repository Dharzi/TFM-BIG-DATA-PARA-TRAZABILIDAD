"""
Descarga el bloque y sus transacciones en dos ficheros json, 
uno para el nodo y otro para todas sus transacciones 

Argumentos:

block_height -- Altura del bloque a descargar
"""

from bitcoinrpc.authproxy import AuthServiceProxy
import json
 
# Configura la conexión RPC con Bitcoin Core
rpc_user = 'usuariorcp'
rpc_password = 'RcpT7m8l0ck'
rpc_port = 8332
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@localhost:{rpc_port}", timeout=60)
 
# Establece la altura del bloque deseado
#block_height = 792726
#block_height = 792727
block_height = 792725

path_bitcoin_cli = '/Blockchain/bitcoin-22.0/bin/'
 
# Obtiene el hash del bloque deseado
block_hash = rpc_connection.getblockhash(block_height)

# Obtiene los detalles del bloque deseado
block_data = rpc_connection.getblock(block_hash)

# Nombre del archivo donde se guardarán los datos de las transacciones
file_name_bloque = '/Blockchain/codigo/json/bloque_previo.json'

# Obtiene los detalles del bloque

with open(file_name_bloque, 'w') as file:
    # Guarda los datos de la transacción en el archivo en formato json
    block_data_json = json.dumps(block_data, default=str)
    file.write(json.dumps(block_data_json, indent=4))
    file.write('\n')

# Obtiene los hashes de las transacciones contenidas en el bloque
transaction_hashes = block_data['tx']

# Nombre del archivo donde se guardarán los datos de las transacciones
file_name_transacciones = '/Blockchain/codigo/json/transacciones_bloque_previo.json'

# Itera sobre cada hash de transacción y utiliza el comando `getrawtransaction` para obtener los datos de la transacción
with open(file_name_transacciones, 'w') as file:
    #for tx_hash in block_data['tx']:
    for tx_hash in transaction_hashes:
        # Obtiene los detalles de cada transacción
        tx_data = rpc_connection.getrawtransaction(tx_hash, True, block_hash)
     
        # Guarda los datos de la transacción en el archivo en formato json
        transaction_data = json.dumps(tx_data, default=str)
        file.write(json.dumps(transaction_data, indent=4))
        file.write('\n')
 	
 	