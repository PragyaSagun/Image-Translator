
def create_translation_request_message(id, sender, region, requester, text, email, m_type="TRAN"):
    """
    Only interface node will ever use create_translation_request_message.
    """
    message = {
        "sender": sender,
        "region": region,
        "requester": requester,
        "id": id,
        "message": text,
        "type": m_type,
        "email": email
    }
    return message


def create_transcription_request_message(id, sender, region, requester, email, image, m_type="TRSC"):
    message = {
        "sender": sender,
        "region": region,
        "requester": requester,
        "id": id,
        "type": m_type,
        "email": email,
        "image": image
    }
    return message


def create_translation_response_message(translation_request, sender, translated_text):
    message = {
        "sender": sender,
        "region": translation_request["region"],
        "requester": translation_request["requester"],
        "id": translation_request["id"],
        "message": translated_text,
        "type": "ACKT"
    }
    return message


def create_duplicate_response():
    message = {
        "message": "This is a duplicate request",
        "type": "DUPL"
    }
    return message


def create_message(sender, nodeid, nodeinfo, id, m_type, node_type="translation", ext_ip="none"):
    message = {
        "sender": sender,
        "id": id,
        "node_info": (nodeid, nodeinfo),
        "type": m_type,
        "ntype": node_type,
        "extip": ext_ip
    }
    return message
