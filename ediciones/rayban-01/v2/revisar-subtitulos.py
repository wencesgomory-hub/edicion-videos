from pathlib import Path
import json
r=Path('/workspace/rayban-01-v2')
# Clear phrases contrasted across large-v3, small, overlapping windows and visual context.
# Ambiguous fragments and the uncorroborated model-only praise are deliberately excluded.
segments=[
(0,2.15,'Tiene una rayita acá...'),(2.15,3.,'¿Eh?'),(3.,4.9,'Esta rayita...'),(4.9,6.,'¿Cuál?'),
(15.,16.6,'¿Esto es cámara?'),(17.,19.1,'Un desastre cómo contestan...'),(19.1,20.,'Vos tenés...'),(20.,22.,'Te contestan...'),(22.,25.,'No tienen como un proceso claro, ¿entendés?'),
(25.,26.,'Claro.'),(26.,28.1,'Cuando me mandaste para reservarlo...'),(28.1,29.6,'Ya lo tenés armado.'),(29.6,32.7,'Sí, sí, lo tratamos de manejar.'),(32.7,34.7,'Sí, el tema es que...'),(34.7,36.6,'Lo voy a usar para eso.'),
(36.6,38.7,'La cámara, fijate que...'),(38.7,45.,'Es una locura lo que la cámara está haciendo.'),(45.,47.2,'Y la batería también dura una locura.'),(47.2,49.7,'Al ser Max, también dura un montonazo.'),
(52.1,54.3,'Lo apago acá arriba.'),(54.3,56.6,'Y ahí va.'),(56.6,61.46,'Cualquier cosa de la configuración, que te trabes o algo, me mandás'),(61.46,62.46,'un mensajito.'),(62.46,63.46,'No pasa nada.'),(63.46,65.86,'Te lo dejo acá. Si querés, metelo acá adentro.'),
(66.,67.1,'La bolsita.'),(67.1,69.25,'Te guardo acá la garantía.'),(69.25,72.4,'La fundita.'),(72.4,74.3,'Ahí entró.'),
(78.,79.7,'Bueno, señor. Un gustazo.'),(79.7,81.2,'Nos estamos viendo.'),(81.2,83.2,'Cualquier cosita me decís.'),(83.2,84.473,'Dale, dale.')]
x=[{'offset':0,'result':{'segment_timestamps':[a for a,b,t in segments],'segment_durations':[b-a for a,b,t in segments],'segment_texts':[t for a,b,t in segments]}}]
(r/'transcript-reviewed.json').write_text(json.dumps(x,ensure_ascii=False,indent=2))
