KITE & WONDER — WONDER JOURNAL

Edytor: https://kite-wonder-website.netlify.app/admin/
Artykuły: https://kite-wonder-website.netlify.app/journal/

DODAWANIE I PUBLIKOWANIE
1. Otwórz edytor i zaloguj się przez GitHub.
2. Wybierz Wonder Journal Articles, następnie New Article.
3. Wpisz Title (tytuł), Publication date (datę), Category (kategorię),
   Summary (krótki opis) i Article (treść). Cover image jest opcjonalne.
4. Szkic: zostaw Show on website wyłączone i użyj Publish / Publish now,
   aby zapisać tekst w repozytorium. Przycisk zapisuje plik; o obecności
   w Journal decyduje przełącznik Show on website.
5. Gotowy artykuł: włącz Show on website i użyj Publish / Publish now.
6. Poczekaj na udane wdrożenie w Netlify (zwykle kilka minut), a potem
   otwórz /journal/. Samo zapisanie w edytorze nie kończy wdrożenia.

EDYCJA I WYCOFANIE
Otwórz artykuł na liście, zmień treść i ponownie zapisz.
Aby wycofać publikację, wyłącz Show on website i zapisz. Po udanym
wdrożeniu zniknie zarówno karta na liście, jak i osobna strona artykułu.
Publication date służy do wyświetlania i sortowania; nie jest harmonogramem.

WAŻNE O SZKICACH
Oba obecne przykładowe teksty pozostają szkicami (published: false).
Nie publikuj ich jako gotowych artykułów. Niewidoczność szkicu w Journal
nie oznacza prywatności: repozytorium GitHub jest publiczne.

DLA OSOBY UTRZYMUJĄCEJ STRONĘ
Źródło produkcyjne: main w KiteWonder/kite-wonder-website.
Netlify: pip install -r requirements.txt && python -m unittest discover -s tests -v && python scripts/build_blog.py
Katalog publikowany: public
Decap: admin/index.html + admin/config.yml; GitHub OAuth obsługuje
 dotychczasowy dostawca Netlify. Sekretów nie umieszczamy w kodzie.
Generator kopiuje admin przy każdym wdrożeniu i generuje /journal/
oraz /journal/<nazwa-pliku>/ tylko dla published: true.
Strona główna index.html i style Journal pozostają bez zmian.

WERSJE PODGLĄDOWE I TESTY
Przed scaleniem zmian do main sprawdź Deploy Preview z pull requestu.
CMS w Deploy Preview zapisuje do gałęzi HEAD tego podglądu, nie do main.
Podgląd używa istniejącej ochrony dostępu Netlify; nie wyłączaj jej do testów.
Testy automatyczne tworzą artykuły wyłącznie w katalogu tymczasowym,
sprawdzają zapis, publikację, edycję, wycofanie, usunięcie i obrazki,
a następnie sprzątają po sobie. Treści testowe nie trafiają do public.

Zmiany na main uruchamiają produkcyjne wdrożenie po stronie Netlify.
Scalanie tej poprawki wymaga wcześniejszego zatwierdzenia właścicielki.
Końcowy test logowania i zapisu przez CMS wymaga zalogowanej sesji GitHub;
pełny test publicznego wdrożenia można zakończyć dopiero po zatwierdzeniu.
