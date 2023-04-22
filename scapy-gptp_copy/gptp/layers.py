from scapy.fields import BitEnumField, BitField, ByteField, ConditionalField, FlagsField, \
        LongField, ShortField, SignedByteField, XBitField, XByteField, XIntField, XStrFixedLenField, SignedShortField
from scapy.layers.l2 import Ether
from scapy.layers.inet import UDP
from scapy.packet import Packet, bind_layers

from .fields import PortIdentityField, TimestampField

PTP_EVENT_UDP_PORT =    319
PTP_GENERAL_UDP_PORT =  320
class PTPv2(Packet):
    name = "PTPv2"

    MSG_TYPES = {
        0x0: "Sync",
        0x1: "DelayRequest",
        0x2: "PdelayReqest",
        0x3: "PdelayResponse",
        0x8: "FollowUp",
        0x9: "DelayResponse",
        0xA: "PdelayResponseFollowUp",
        0xB: "Announce",
        0xC: "Signaling",
        0xD: "Managment"
    }

    FLAGS = [
        "LI61", "LI59", "UTC_REASONABLE", "TIMESCALE",
        "TIME_TRACEABLE", "FREQUENCY_TRACEABLE", "?", "?",
        "ALTERNATE_MASTER", "TWO_STEP", "UNICAST", "?",
        "?", "profileSpecific1", "profileSpecific2", "SECURITY",
    ]

    fields_desc = [
        BitField("transportSpecific", 1, 4),
        BitEnumField("messageType", 0, 4, MSG_TYPES),
        XBitField("minorVersionPTP", 0, 4),
        BitField("versionPTP", 0x2, 4),
        ShortField("messageLength", 34),
        ByteField("domainNumber", 0),
        XByteField("reserved1", 0),
        FlagsField("flags", 0, 16, FLAGS),
        LongField("correctionField", 0),
        XIntField("reserved2", 0),
        PortIdentityField("sourcePortIdentity", 0),
        ShortField("sequenceId", 0),
        XByteField("control", 0),
        SignedByteField("logMessageInterval", -3),

        # Announce
        ConditionalField(TimestampField("originTimestamp_announce", 0), lambda pkt: pkt.is_announce),
        ConditionalField(SignedShortField("currentUtcOffset", 0), lambda pkt: pkt.is_announce),
        ConditionalField(BitField("reserved", 0, 8), lambda pkt: pkt.is_announce),
        ConditionalField(ByteField("grandmasterPriority1", 0), lambda pkt: pkt.is_announce),
        ConditionalField(BitField("grandmasterClockQuality", 0, 32), lambda pkt: pkt.is_announce),
        ConditionalField(ByteField("grandmasterPriority2", 0), lambda pkt: pkt.is_announce),
        ConditionalField(BitField("grandmasterIdentity", 0, 64), lambda pkt: pkt.is_announce),
        ConditionalField(ShortField("stepsRemoved", 0), lambda pkt: pkt.is_announce),
        ConditionalField(BitField("timeSource", 0, 8), lambda pkt: pkt.is_announce),

        # Sync
        ConditionalField(TimestampField("originTimestamp_sync", 0), lambda pkt: pkt.is_sync),

        #DelayResponse
        ConditionalField(TimestampField("receiveTimestamp", 0), lambda pkt: pkt.is_delay_response),
        ConditionalField(PortIdentityField("requestingPortIdentity_delayResponse", 0), lambda pkt: pkt.is_delay_response),

        # FollowUp
        ConditionalField(TimestampField("preciseOriginTimestamp", 0), lambda pkt: pkt.is_followup),
        #ConditionalField(XStrFixedLenField("informationTlv", 0, 32), lambda pkt: pkt.is_followup),

        # PdelayReq
        ConditionalField(TimestampField("originTimestamp_PdelayReq", 0), lambda pkt: pkt.is_pdelay_req),
        ConditionalField(BitField("reserved_PdelayReq", 0, 80), lambda pkt: pkt.is_pdelay_req),

        # PdelayResp
        ConditionalField(TimestampField("requestReceiptTimestamp", 0),lambda pkt: pkt.is_pdelay_resp),
        ConditionalField(PortIdentityField("requestingPortIdentity_PdelayResp", 0), lambda pkt: pkt.is_pdelay_resp),

        # PdelayRespFollowUp
        ConditionalField(
            TimestampField("responseOriginTimestamp", 0),
            lambda pkt:pkt.is_pdelay_resp_followup),

        ConditionalField(
            PortIdentityField("requestingPortIdentity", 0),
            lambda pkt: pkt.is_pdelay_resp or pkt.is_pdelay_resp_followup),
    ]

    @property
    def is_sync(self):
        return(self.messageType == 0x0)

    @property
    def is_followup(self):
        return(self.messageType == 0x8)

    @property
    def is_pdelay_req(self):
        return(self.messageType == 0x2)

    @property
    def is_pdelay_resp(self):
        return(self.messageType == 0x3)

    @property
    def is_pdelay_resp_followup(self):
        return(self.messageType == 0xA)
    
    @property
    def is_announce(self):
        return(self.messageType == 0xB)
    
    @property
    def is_delay_response(self):
        return(self.messageType == 0x9)

    def extract_padding(self, s):
        return "", s


bind_layers(Ether, PTPv2, type=0x88F7)
#bind_layers(UDP, PTPv2, sport = PTP_EVENT_UDP_PORT)
#bind_layers(UDP, PTPv2, sport = PTP_GENERAL_UDP_PORT)
