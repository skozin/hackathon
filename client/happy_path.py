import uuid
import json
import asyncio
import websockets
import urllib.parse
import crypto


wc_bridge_uri = 'wss://uniswap.bridge.walletconnect.org/?env=browser&host=app.uniswap.org&protocol=wc&version=1'


def generate_uuid():
    return str(uuid.uuid4())


def get_displayed_uri(topic, uri, key, version = 1):
    encoded_uri = urllib.parse.quote(uri, safe='')
    return f'wc:{topic}@{version}?bridge={uri}&key={key}'


def get_websocket_message(topic, topic_type, payload, silent = True):
    return {
        'topic': topic,
        'type': topic_type,
        'payload': payload,
        'silent': silent
    }


def get_wc_session_request(rpc_id, peer_id, peer_meta, chain_id = 1):
    return {
        'id': rpc_id,
        'jsonrpc': '2.0',
        'method': 'wc_sessionRequest',
        'params': [{
            'peerId': peer_id,
            'peerMeta': peer_meta,
            'chainId': chain_id
        }]
    }


def decode_message_payload(payload):
    parsed_json = json.loads(payload)

    data = parsed_json['data']
    hmac = parsed_json['hmac']
    iv = parsed_json['iv']

    return {
        'some': data
    }


def get_qr_link(uri):
    qr_data = { 'data': uri }
    qr_data_encoded = urllib.parse.urlencode(qr_data)
    return f'https://api.qrserver.com/v1/create-qr-code/?size=300x300&{qr_data_encoded}'


async def wc_test():
    async with websockets.connect(wc_bridge_uri) as websocket:
        rpc_id = 0
        peer_id = generate_uuid()
        handshake_uuid = generate_uuid()

        key = crypto.generate_key()
        hex_key = key.hex()

        peer_meta = {
            'name': 'test app'
        }


        url_encoded = urllib.parse.quote('https://uniswap.bridge.walletconnect.org', safe='')
        wc_uri = 'wc:64896842-9de7-49a6-b02f-86846a304832@1?bridge=https%3A%2F%2Funiswap.bridge.walletconnect.org&key=6990358dc06e87f4b9c27999cf9eecb866a95de6bfe35dbb40204811b2fc3f49'

        print('rpc_id:', rpc_id)
        print('peer_id:', peer_id)
        print('handshake_uuid:', handshake_uuid)
        print('key:', hex_key)
        print('peer_meta:', peer_meta)
        print('wc_uri:', wc_uri)
        print('get_qr_link:', get_qr_link(wc_uri))


        print()

        name = input('Go? ')

        wc_request = get_wc_session_request(rpc_id, peer_id, peer_meta)
        rpc_id = rpc_id + 1

        wc_request_string = json.dumps(wc_request)
        wc_request_str_bytes = b'' + bytearray(wc_request_string, 'utf8')

        payload = crypto.encrypt(wc_request_str_bytes, key)

        payload['data'] = payload['data'].hex()
        payload['hmac'] = payload['hmac'].hex()
        payload['iv'] = payload['iv'].hex()

        initial_message = get_websocket_message(handshake_uuid, 'pub', json.dumps(payload))
        subscribe_message = get_websocket_message(peer_id, 'sub', '')

        print('wc_request message', json.dumps(initial_message))
        print('sub', json.dumps(subscribe_message))

        await websocket.send(json.dumps(initial_message))
        await websocket.send(json.dumps(subscribe_message))

        resp = await websocket.recv()
        print(f'< {resp}')

        ack_message = get_websocket_message(peer_id, 'ack', '')
        await websocket.send(json.dumps(ack_message))


asyncio.get_event_loop().run_until_complete(wc_test())
