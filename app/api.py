import json,os
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from app.modelo import Modelo,ROOT
MODEL=Modelo()
RULES={
'no_acreditado':('R01','Verificar referencia, fecha y comprobante del pago antes de confirmar su acreditación.'),
'duplicado':('R02','Comparar las referencias de ambos cargos y verificar si corresponden a una misma instrucción.'),
'devolucion':('R03','Revisar el motivo del rechazo o cancelación y validar el soporte de la devolución.')}
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def send(self,code,obj):
        b=json.dumps(obj,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
    def do_GET(self):
        if self.path=='/health':return self.send(200,{'estado':'ok','modelo':MODEL.m['version']})
        if self.path=='/':
            b=(ROOT/'app/index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(b)));self.end_headers();return self.wfile.write(b)
        return self.send(404,{'error':'Ruta no encontrada'})
    def do_POST(self):
        if self.path!='/predict':return self.send(404,{'error':'Ruta no encontrada'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':return self.send(415,{'error':'Se requiere application/json'})
        try:n=int(self.headers.get('Content-Length','0'))
        except ValueError:return self.send(400,{'error':'Longitud incorrecta'})
        if n>16384:return self.send(413,{'error':'Solicitud demasiado grande'})
        if n<=0:return self.send(400,{'error':'Cuerpo vacío'})
        try:body=json.loads(self.rfile.read(n))
        except (ValueError,UnicodeError):return self.send(400,{'error':'JSON inválido'})
        if not isinstance(body,dict) or set(body)!={'texto'}:return self.send(422,{'error':'Se requiere solamente el campo texto'})
        t=body['texto']
        if not isinstance(t,str) or not 5<=len(t.strip())<=2000:return self.send(422,{'error':'texto debe contener entre 5 y 2000 caracteres'})
        c,conf=MODEL.predict(t)
        if c:
            rid,rule=RULES[c];evidence=[{'id':rid,'fuente':'Reglas académicas simuladas versión 1','texto':rule}]
            draft='Propuesta para revisión del analista. '+rule+' No se ha confirmado ningún movimiento monetario.'
        else:evidence=[];draft='No cuento con evidencia suficiente para proponer una categoría. Solicito revisión del analista.'
        return self.send(200,{'categoria':c or 'revision_manual','confianza':conf,'requiere_revision':True,'evidencia':evidence,'borrador':draft,'modelo':MODEL.m['version']})
if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','8000'))),Handler).serve_forever()
