import sys
import Router.Logger as Logger
import KSR as KSR
from concurrent import futures
import logging
import grpc

def dumpObj(obj):
    for attr in dir(obj):
        # KSR.info("obj.%s = %s\n" % (attr, getattr(obj, attr)))
        Logger.LM_INFO("obj.%s = %s\n" % (attr, getattr(obj, attr)))

# Global function to instantiate a Kamailio class object
# -- executed when Kamailio app_python module is initialized
def mod_init():
    KSR.info("===== from Python mod init\n")
    return kamailio()

# Kamailio class definition
in_conference=list()
class kamailio:
    def __init__(self):
        KSR.info('===== kamailio.__init__\n')
    
    # Executed when Kamailio child processes are initialized
    def child_init(self, rank):
        KSR.info('===== kamailio.child_init(%d)\n' % rank)
        return 0

    # SIP request routing
    # -- equivalent of request_route{}
    def ksr_request_route(self, msg):

        
        # Verificar se o domínio é válido
        if not KSR.pv.get("$fu").endswith("@acme.pt"):
            KSR.info(f"Negado: {KSR.pv.get('$fu')}")
            KSR.sl.send_reply(403, "Forbidden")
            return 1

        # Verificação do método SIP
        if msg.Method == "REGISTER":
            KSR.info("Processando registo de funcionário_...\n")
            KSR.registrar.save("location", 0)  
            return 1
        
        
        if (msg.Method == "INVITE"):
            
            
            if KSR.pv.get("$tu") == "sip:conferencia@acme.pt":
                KSR.pv.sets("$ru","sip:inconference@127.0.0.1:5080")
                in_conference.append(KSR.pv.get("$fu"))
                print(f"Halo + {str(in_conference)}")
                status_code = KSR.pv.get("$fu")
                KSR.info(f"Status da resposta_Entrei aqui cralho: {status_code}\n")


                KSR.tm.t_relay()
                return 1
            
            
          #  if KSR.pv.get("$rs") == "486":
           #     KSR.info("Redirecionando chamada para servidor de anuncios")
            #    KSR.pv.sets("$ru", "busyann@127.0.0.1:5080")
             #   KSR.tm.t_relay()
              #  return 1
                
                
                
            if KSR.registrar.lookup("location") == 1:
                

                if(KSR.pv.get("$to") in in_conference ):
                   KSR.pv.sets("$ru","sip:inconference@127.0.0.1:5080")
                   KSR.info("Entrei aqui")
                   KSR.tm.t_relay()
                   return 1
              


                KSR.info("Passando a chamada")
                KSR.tm.t_relay()
                return 1
            else:
                KSR.info("Destino não encontrado")
                KSR.sl.send_reply(404, "User not found")  
                return 1 
            
            
            
            
            if KSR.pv.get("$si") == "in_conference":
                KSR.info("In conference here")
                KSR.pv.sets("$ru","sip:inconference@127.0.0.1:5080")
                KSR.tm.t_relay()
                return 1

            

        if msg.Method == "ACK":
           # KSR.info("ACK R-URI:" + KSR.pv.get("$ru") + "\n")
           # KSR.tm.t_relay()
            return 1
        
    def ksr_reply_route(self, msg):
        KSR.info("===== Resposta SIP - de Kamailio Python\n")
        
        # Captura o código de status da resposta SIP
        status_code = KSR.pv.get("$rs")
        KSR.info(f"Status da resposta_este: {status_code}\n")

        # Verifica se a resposta SIP foi "486 Busy Here"
        if status_code == "486":  # "Busy Here"
            KSR.info("Redirecionando chamada para servidor de anúncios (Busy Here)\n")
            KSR.pv.sets("$ru", "busyann@127.0.0.1:5080")
            KSR.tm.t_relay()
            return 1

        # Se a resposta for qualquer outro código, apenas continue
        return 1

    def ksr_onsend_route(self, msg):
        KSR.info("Trying to connect to: %s" % KSR.pv.get("$to"))
        
        KSR.info("===== onsend route - from kamailio python script\n")
        KSR.info("      %s\n" % (msg.Type))
        return 1
