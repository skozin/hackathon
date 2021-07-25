import uuid
import json
import asyncio
import websockets
import urllib.parse
import crypto
import re


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


def hit_with_a_hammer(resp):
    r_json = json.loads(str(resp))
    r_json['payload'] = json.loads(r_json['payload'])
    return r_json


def decrypt_message(payload, key):
    print('pk', payload, key)

    data = bytearray.fromhex(payload['data'])
    iv = bytearray.fromhex(payload['iv'])
    hmac = bytearray.fromhex(payload['hmac'])

    decrypted_payload = crypto.decrypt(
        data,
        iv,
        hmac,
        key
    )

    return json.loads(decrypted_payload.decode('utf-8'))


def get_sign_request(rpc_id, tx):
    return {
        'id': rpc_id,
        'jsonrpc': '2.0',
        'method': 'eth_signTransaction',
        'params': [tx]
    }


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
        wc_uri = get_displayed_uri(handshake_uuid, url_encoded, hex_key)

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

        json_resp = hit_with_a_hammer(resp)
        print('resp', json_resp)

        decrypted_payload = decrypt_message(json_resp['payload'], key)
        print('decrypted_payload', decrypted_payload)

        account = decrypted_payload['result']['accounts'][0]
        nounce = 10

        print('account', account)

        ack_message = get_websocket_message(peer_id, 'ack', '')
        await websocket.send(json.dumps(ack_message))

        tx = {
            'from': account,
            'to': '0x89D24A7b4cCB1b6fAA2625Fe562bDd9A23260359',
            'data': '0x',
            'gasPrice': '0x02540be400',
            'gas': '0x9c40',
            'value': '0x00',
            'nonce': '0x0114',
        }
        print('tx', tx)
        sign_request = get_sign_request(rpc_id, tx)
        rpc_id = rpc_id + 1

        sign_request_string = json.dumps(sign_request)
        sign_request_string_bytes = b'' + bytearray(sign_request_string, 'utf8')

        payload = crypto.encrypt(sign_request_string_bytes, key)

        payload['data'] = payload['data'].hex()
        payload['hmac'] = payload['hmac'].hex()
        payload['iv'] = payload['iv'].hex()

        sign_message = get_websocket_message(peer_id, 'pub', json.dumps(payload), False)

        print('sign_message', sign_message)
        print('sign_message', json.dumps(sign_message))
        await websocket.send(json.dumps(sign_message))

        resp = await websocket.recv()
        print(f'< {resp}')



asyncio.get_event_loop().run_until_complete(wc_test())
