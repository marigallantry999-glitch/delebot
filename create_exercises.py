import json
import os

# Создаём папку exercises если её нет
os.makedirs("data/exercises", exist_ok=True)

# Твои правила с упражнениями
RULES_DATA = {
    "rules": [
        {
            "rule": "Ser vs Estar",
            "file_name": "ser_estar",
            "exercises": [
                {"type": "translation", "question": "Она врач.", "answer": "Ella es médica."},
                {"type": "translation", "question": "Мы устали.", "answer": "Estamos cansados."},
                {"type": "translation", "question": "Это моя книга.", "answer": "Este es mi libro."},
                {"type": "fill_in", "question": "Mis amigos _______ en la playa.", "answer": "están"},
                {"type": "fill_in", "question": "El café _______ caliente.", "answer": "está"},
                {"type": "fill_in", "question": "_______ las dos de la tarde.", "answer": "Son"},
                {"type": "correct", "question": "Ella está alta y rubia.", "answer": "Ella es alta y rubia."},
                {"type": "correct", "question": "Hoy es nublado.", "answer": "Hoy está nublado."},
                {"type": "correct", "question": "Nosotros somos en el cine.", "answer": "Nosotros estamos en el cine."}
            ]
        },
        {
            "rule": "Hay vs Está",
            "file_name": "hay_esta",
            "exercises": [
                {"type": "translation", "question": "В парке есть дети.", "answer": "Hay niños en el parque."},
                {"type": "translation", "question": "Мой друг в кафе.", "answer": "Mi amigo está en el café."},
                {"type": "translation", "question": "На столе есть яблоко.", "answer": "Hay una manzana en la mesa."},
                {"type": "fill_in", "question": "_______ tres gatos en el jardín.", "answer": "Hay"},
                {"type": "fill_in", "question": "El libro _______ en la mochila.", "answer": "está"},
                {"type": "fill_in", "question": "_______ mucha gente en la fiesta.", "answer": "Hay"},
                {"type": "correct", "question": "Está dos sillas en la cocina.", "answer": "Hay dos sillas en la cocina."},
                {"type": "correct", "question": "Hay mi hermana en la habitación.", "answer": "Mi hermana está en la habitación."},
                {"type": "correct", "question": "¿Hay tu teléfono aquí?", "answer": "¿Está tu teléfono aquí?"}
            ]
        },
        {
            "rule": "Gerundio",
            "file_name": "gerundio",
            "exercises": [
                {"type": "translation", "question": "Я читаю книгу.", "answer": "Estoy leyendo un libro."},
                {"type": "translation", "question": "Они обедают сейчас.", "answer": "Ellos están almorzando ahora."},
                {"type": "translation", "question": "Мы учим испанский.", "answer": "Estamos aprendiendo español."},
                {"type": "fill_in", "question": "Mi madre _______ (cocinar) la cena.", "answer": "está cocinando"},
                {"type": "fill_in", "question": "Los niños _______ (jugar) en el parque.", "answer": "están jugando"},
                {"type": "fill_in", "question": "Yo _______ (escribir) una carta.", "answer": "estoy escribiendo"},
                {"type": "correct", "question": "Él está leyendo y comiendo.", "answer": "Él está leyendo y comiendo."},
                {"type": "correct", "question": "Nosotros estamos bebiendo agua.", "answer": "Nosotros estamos bebiendo agua."},
                {"type": "correct", "question": "Ellos están durmiendo.", "answer": "Ellos están durmiendo."}
            ]
        },
        {
            "rule": "Preposiciones (a, de, en, por, para, sobre)",
            "file_name": "preposiciones",
            "exercises": [
                {"type": "translation", "question": "Voy a la escuela.", "answer": "Voy a la escuela."},
                {"type": "translation", "question": "El regalo es para María.", "answer": "El regalo es para María."},
                {"type": "translation", "question": "El libro está sobre la mesa.", "answer": "El libro está sobre la mesa."},
                {"type": "fill_in", "question": "Salgo _______ mi casa _______ las ocho.", "answer": "de, a"},
                {"type": "fill_in", "question": "Este regalo es _______ ti.", "answer": "para"},
                {"type": "fill_in", "question": "Vivo _______ una ciudad pequeña.", "answer": "en"},
                {"type": "correct", "question": "Voy por el cine.", "answer": "Voy al cine."},
                {"type": "correct", "question": "El lápiz es de Juan.", "answer": "El lápiz es de Juan."},
                {"type": "correct", "question": "Camino para la tienda.", "answer": "Camino a la tienda."}
            ]
        },
        {
            "rule": "Género y número",
            "file_name": "genero_numero",
            "exercises": [
                {"type": "translation", "question": "Столы большие.", "answer": "Las mesas son grandes."},
                {"type": "translation", "question": "Дом красивый.", "answer": "La casa es bonita."},
                {"type": "translation", "question": "Книги интересные.", "answer": "Los libros son interesantes."},
                {"type": "fill_in", "question": "_______ (el/la) problema es difícil.", "answer": "El"},
                {"type": "fill_in", "question": "_______ (un/una) día soleado.", "answer": "Un"},
                {"type": "fill_in", "question": "_______ (los/las) flores son rojas.", "answer": "Las"},
                {"type": "correct", "question": "El mano está lastimado.", "answer": "La mano está lastimada."},
                {"type": "correct", "question": "Unas perros son grandes.", "answer": "Unos perros son grandes."},
                {"type": "correct", "question": "La problema es grave.", "answer": "El problema es grave."}
            ]
        },
        {
            "rule": "Concordancia de adjetivos",
            "file_name": "concordancia",
            "exercises": [
                {"type": "translation", "question": "Мой лучший друг.", "answer": "Mi mejor amigo."},
                {"type": "translation", "question": "Las chicas son inteligentes.", "answer": "Las chicas son inteligentes."},
                {"type": "translation", "question": "El perro es negro.", "answer": "El perro es negro."},
                {"type": "fill_in", "question": "Los gatos son _______ (rápido).", "answer": "rápidos"},
                {"type": "fill_in", "question": "Mi hermana es _______ (alto).", "answer": "alta"},
                {"type": "fill_in", "question": "Las casas son _______ (blanco).", "answer": "blancas"},
                {"type": "correct", "question": "La casa es grande.", "answer": "La casa es grande."},
                {"type": "correct", "question": "Los niños son feliz.", "answer": "Los niños son felices."},
                {"type": "correct", "question": "Mis amigas son simpático.", "answer": "Mis amigas son simpáticas."}
            ]
        },
        {
            "rule": "Pretérito Indefinido",
            "file_name": "preterito_indefinido",
            "exercises": [
                {"type": "translation", "question": "Ayer fui al mercado.", "answer": "Ayer fui al mercado."},
                {"type": "translation", "question": "Ellos comieron pizza.", "answer": "Ellos comieron pizza."},
                {"type": "translation", "question": "Ella llegó tarde.", "answer": "Ella llegó tarde."},
                {"type": "fill_in", "question": "Yo _______ (hablar) con mi jefe.", "answer": "hablé"},
                {"type": "fill_in", "question": "Tú _______ (comer) pollo.", "answer": "comiste"},
                {"type": "fill_in", "question": "Él _______ (vivir) en Madrid.", "answer": "vivió"},
                {"type": "correct", "question": "Ella estudiaba toda la noche.", "answer": "Ella estudió toda la noche."},
                {"type": "correct", "question": "Nosotros fuimos al cine ayer.", "answer": "Nosotros fuimos al cine ayer."},
                {"type": "correct", "question": "Ellos abrieron la ventana.", "answer": "Ellos abrieron la ventana."}
            ]
        },
        {
            "rule": "Imperativo",
            "file_name": "imperativo",
            "exercises": [
                {"type": "translation", "question": "¡Habla más despacio!", "answer": "¡Habla más despacio!"},
                {"type": "translation", "question": "¡Escribe tu nombre!", "answer": "¡Escribe tu nombre!"},
                {"type": "translation", "question": "¡No corras en la casa!", "answer": "¡No corras en la casa!"},
                {"type": "fill_in", "question": "_______ (cerrar) la puerta, por favor.", "answer": "Cierra"},
                {"type": "fill_in", "question": "_______ (venir) a mi fiesta.", "answer": "Ven"},
                {"type": "fill_in", "question": "No _______ (tocar) eso.", "answer": "toques"},
                {"type": "correct", "question": "¡Haces la tarea!", "answer": "¡Haz la tarea!"},
                {"type": "correct", "question": "¡Dices la verdad!", "answer": "¡Di la verdad!"},
                {"type": "correct", "question": "¡Pones el libro aquí!", "answer": "¡Pon el libro aquí!"}
            ]
        },
        {
            "rule": "Pronombres OD/OI",
            "file_name": "pronombres",
            "exercises": [
                {"type": "translation", "question": "Ella me llama.", "answer": "Ella me llama."},
                {"type": "translation", "question": "Te compro un regalo.", "answer": "Te compro un regalo."},
                {"type": "translation", "question": "Lo veo en la calle.", "answer": "Lo veo en la calle."},
                {"type": "fill_in", "question": "Juan _______ (me/te/lo) da el libro.", "answer": "me"},
                {"type": "fill_in", "question": "_______ (nos/os/los) escucha el profesor.", "answer": "nos"},
                {"type": "fill_in", "question": "La carta, _______ (la/lo/las) escribo yo.", "answer": "la"},
                {"type": "correct", "question": "Yo te veo a ti.", "answer": "Yo te veo a ti."},
                {"type": "correct", "question": "Ella lo llama a él.", "answer": "Ella lo llama a él."},
                {"type": "correct", "question": "Nosotros los compramos las flores.", "answer": "Nosotros las compramos."}
            ]
        },
        {
            "rule": "Verbos reflexivos",
            "file_name": "reflexivos",
            "exercises": [
                {"type": "translation", "question": "Yo me levanto temprano.", "answer": "Yo me levanto temprano."},
                {"type": "translation", "question": "Ella se viste rápido.", "answer": "Ella se viste rápido."},
                {"type": "translation", "question": "Nosotros nos bañamos.", "answer": "Nosotros nos bañamos."},
                {"type": "fill_in", "question": "Tú _______ (acostarse) tarde.", "answer": "te acuestas"},
                {"type": "fill_in", "question": "Él _______ (despertarse) a las ocho.", "answer": "se despierta"},
                {"type": "fill_in", "question": "Yo _______ (divertirse) mucho.", "answer": "me divierto"},
                {"type": "correct", "question": "Ellos se lavan los manos.", "answer": "Ellos se lavan las manos."},
                {"type": "correct", "question": "Yo me acuesto a las diez.", "answer": "Yo me acuesto a las diez."},
                {"type": "correct", "question": "Ella despierta a las siete.", "answer": "Ella se despierta a las siete."}
            ]
        },
        {
            "rule": "Perífrasis verbales (ir a, tener que, hay que, poder, querer)",
            "file_name": "perifrasis",
            "exercises": [
                {"type": "translation", "question": "Voy a viajar mañana.", "answer": "Voy a viajar mañana."},
                {"type": "translation", "question": "Tienes que estudiar.", "answer": "Tienes que estudiar."},
                {"type": "translation", "question": "Hay que pagar la cuenta.", "answer": "Hay que pagar la cuenta."},
                {"type": "fill_in", "question": "Nosotros _______ (tener que) trabajar hoy.", "answer": "tenemos que"},
                {"type": "fill_in", "question": "Ellos _______ (querer) comer pizza.", "answer": "quieren"},
                {"type": "fill_in", "question": "_______ (hay que / tener que) limpiar la casa.", "answer": "Hay que"},
                {"type": "correct", "question": "Él va ir al médico.", "answer": "Él va a ir al médico."},
                {"type": "correct", "question": "Puedo ayudar te.", "answer": "Puedo ayudarte."},
                {"type": "correct", "question": "Hay que hacer ejercicio.", "answer": "Hay que hacer ejercicio."}
            ]
        },
        {
            "rule": "Comparativos (más... que, tan... como, menos... que)",
            "file_name": "comparativos",
            "exercises": [
                {"type": "translation", "question": "Soy más alto que tú.", "answer": "Soy más alto que tú."},
                {"type": "translation", "question": "Ella es tan simpática como yo.", "answer": "Ella es tan simpática como yo."},
                {"type": "translation", "question": "Este libro es menos interesante.", "answer": "Este libro es menos interesante."},
                {"type": "fill_in", "question": "Mi coche es _______ rápido _______ el tuyo.", "answer": "más, que"},
                {"type": "fill_in", "question": "Juan es _______ alto _______ Pedro.", "answer": "tan, como"},
                {"type": "fill_in", "question": "Esta ciudad es _______ grande _______ Madrid.", "answer": "menos, que"},
                {"type": "correct", "question": "Ella es más inteligente que yo.", "answer": "Ella es más inteligente que yo."},
                {"type": "correct", "question": "Este café es tan bueno como aquel.", "answer": "Este café es tan bueno como aquel."},
                {"type": "correct", "question": "Tengo menos dinero que tú.", "answer": "Tengo menos dinero que tú."}
            ]
        },
        {
            "rule": "Muy vs Mucho",
            "file_name": "muy_mucho",
            "exercises": [
                {"type": "translation", "question": "La sopa está muy caliente.", "answer": "La sopa está muy caliente."},
                {"type": "translation", "question": "Tengo mucho dinero.", "answer": "Tengo mucho dinero."},
                {"type": "translation", "question": "Hay mucha gente aquí.", "answer": "Hay mucha gente aquí."},
                {"type": "fill_in", "question": "Estoy _______ cansado.", "answer": "muy"},
                {"type": "fill_in", "question": "Bebo _______ agua.", "answer": "mucha"},
                {"type": "fill_in", "question": "Ellos comen _______ pan.", "answer": "mucho"},
                {"type": "correct", "question": "Ella es mucho inteligente.", "answer": "Ella es muy inteligente."},
                {"type": "correct", "question": "Hay muy personas en la fiesta.", "answer": "Hay muchas personas en la fiesta."},
                {"type": "correct", "question": "Tengo muy hambre.", "answer": "Tengo mucha hambre."}
            ]
        }
    ]
}

# Создаём JSON-файлы для каждого правила
for rule_data in RULES_DATA["rules"]:
    file_name = rule_data["file_name"]
    exercises = rule_data["exercises"]
    
    file_path = f"data/exercises/{file_name}.json"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(exercises, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Создан файл: {file_path} ({len(exercises)} упражнений)")

print("\n🎉 Все файлы упражнений созданы!")
print(f"📁 Папка: data/exercises/")
print(f"📊 Всего правил: {len(RULES_DATA['rules'])}")
print(f"📝 Всего упражнений: {sum(len(r['exercises']) for r in RULES_DATA['rules'])}")