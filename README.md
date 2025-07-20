# Zombicide

Un simulador desarrollado en python  
Fecha comienzo: 31 mayo 2025

Aqui voy a ir poniendo las ideas del juego  
Comienzo con estructurar todas las partes del juego

Objetos:

* Personajes: nombre, clase, heridas, xp, acciones totales, acciones restantes, habilidades, equipo, armas  
* Zombies: tipo, daño límite, daño infligido, acciones  
* Equipo: id, descripción, efectos  
* Armas: rango, dados, target, daño, nivel mínimo, recarga, abre puertas, ruido  
* Habilidades: consumo acciones, efectos  
* Coches: plazas, movimiento

Menú principal

1. Empezar partida  
   1. Seleccionar juego (zombicide original, expansión)  
   2. Seleccionar escenario  
2. Cargar partida  
3. Salir

Preparación

1. Dibujar mapa  
   1. Seleccionar módulos, rotarlos, colocarlos.  
   2. Colocar módulos.  
   3. Colocar objetos de mapa: salidas zombie, objetivos, puertas, zombies, exit, coches, salida supervivientes  
2. Crear mazo cartas equipo  
3. Crear mazo cartas zombie  
4. Supervivientes: resetear heridas, equipo inicial, XP  
5. Determinar primer turno y orden de turnos

Turno

1. Turno personajes  
   1. Seleccionar primer superviviente  
   2. Contar acciones disponibles  
   3. Ejecutar acción  
   4. Restar acciones disponibles  
2. Turno zombies  
   1. Movimiento  
      1. Determinar zona destino  
         1. Seleccionar zona con zombies  
         2. Superviviente en línea de visión  
         3. Mayor nivel de ruido  
         4. Determinar ruta más corta  
         5. Mover zombie  
      2. Mover   
   2. Atacar  
      1. Aplicar daño  
      2. Chequear si mata supervivientes  
      3. Chequear si fin de partida  
   3. Cartas zombie (por cada salida zombie)  
      1. Sacar carta aleatoria de mazo  
      2. Poner zombies  
      3. Asignar ID a cada zombie en el tablero  
3. Cierre  
   1. Mover ficha primer turno

Acciones:

1. Movimiento  
   1. Chequea movimiento: a dónde se puede mover (ilumina las zonas posibles)  
   2. Chequeo de zona con zombies  
   3. Mover superviviente  
2. Atacar  
   1. Chequea ataque: en qué zonas puede atacar según armas  
   2. Chequea posibilidad usar arma  
   3. Chequea línea de visión (para ataque a distancia)  
   4. Chequeo de distancia a zombie (para ataque a rango)  
   5. Resolución ataque  
      1. Tirar dados  
      2. Contar éxitos  
      3. Aplicar éxitos a zombies (elegir por jugador)  
      4. Quitar zombies muertos  
      5. Aplicar XP (cambio de color?) → cambio nivel superviviente  
3. Intercambiar objetos  
   1. Chequea si puede intercambiar objetos  
   2. Cambiar objetos  
4. Hacer ruido → añadir ficha de ruido  
5. Abrir puerta  
   1. Chequea si puede abrir puerta  
   2. Abrir puerta, marcarla como abierta en mapa  
6. Usar objeto  
7. Usar habilidad  
   1. Chequea posibilidad de usar habilidad  
8. Buscar  
   1. Sacar una carta de equipo  
   2. Colocar la carta en ficha personaje o eliminar una

Módulos

1. Son módulos 3 x 3 celdas  
2. Atributos de cada celda: edificio, calle…  
3. Conexiones: abierto, cerrado (pared), puerta  
4. Objetos: alcantarilla, objetivo…

