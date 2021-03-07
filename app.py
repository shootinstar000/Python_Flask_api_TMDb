'''
Desarrollo de prueba de web-site con la API de The Movie Database (TMDb) version 3 con
el framework FLASK de Python, en el se puede realizar busquedas por nombre de tv-series,
temporadas asociadas a las serie y sus episodios. O busquedas de peliculas, encontrarlas
por a;o, recomendaciones basadas en una pelicula. Tendencia de la temporada.

Api v3 TMDb muy completa y funcional que provee amplio desarrollo de busquedas.
Libreria tmdbv3api excelente y bastante facil de usar.

nota:
El archivo de python se puede estructurar el modulos al igual que la API_KEY de la API
para hacerlos mas seguros, sin embargo lo dise;o en un solo archivo para hacerlo legible
por ser la primera version bastante aceptable. :)

Version 0.1
Desarrollado por Eddie Espinoza

'''

import datetime
from flask import Flask, request, redirect, render_template, jsonify, url_for
from tmdbv3api import TMDb
from tmdbv3api import Movie, Discover, Trending, TV, Season, Episode
from werkzeug.routing import BaseConverter
#from flask_bootstrap import Bootstrap

app = Flask(__name__)

tmdb = TMDb()
tmdb.api_key = 'YOUR_API_KEY_HERE'

tmdb.language = 'en'
tmdb.debug = True

url_api_tmdb ='https://api.themoviedb.org/3' #URL API
url_img_base = 'https://image.tmdb.org/t/p/w342' #URL for images

movie = Movie()
discover = Discover()
trending = Trending()
tv = TV()
season = Season()
episode = Episode()

def get_genres(id):
    ''' 
    Obtiene lista de generos para las peliculas
    '''
    searchs_details = movie.details(id)
    genre_list = []
    for i in range(len(searchs_details.genres)):
        genre_list.append(searchs_details.genres[i]['name'])
    genre = ", ".join(genre_list) # se obtiene lista sin corchetes
       
    return genre

@app.route('/trending')
def trendAll():
    # obtiene la lista de peliculas y series en tendencia
    trends = trending.all_week()    
    
    return render_template('trending.html', url_img_base = url_img_base, trends = trends)

@app.route('/movie_trend')
def trendMovie():
    # Obtiene la lista de peliculas de la semana
    listTrendMovie = trending.movie_week()

    return render_template('movie_trend.html', url_img_base = url_img_base, listTrendMovie = listTrendMovie)

@app.route('/tv_trend')
def trendTv():
    #Obtiene la lista de series de Tv de la semana
    listTrendTv = trending.tv_week()

    return render_template('tv_trend.html', url_img_base = url_img_base, listTrendTv = listTrendTv)

@app.route('/')
def index():
    # HOME
    
    return trendAll()

@app.route('/popularity')
def popularity():
    # obtiene la lista de peliculas populares para la fecha
    populars = movie.popular()

    return render_template('popularity.html', populars = populars, url_img_base = url_img_base)

@app.route('/movie', methods=['GET','POST'])
def findMovie(): 
    # obtiene las peliculas basadas en la solicyud del usurio   
    try: 
        if request.method == 'GET':
            return trendMovie()
        search_list = []        
        if request.method == 'POST':
            title = request.form['Title']
            
            if len(title) > 0:
                search_list = movie.search(title) 
                        
            else:
                searchNo = 'No Search'
                return render_template('movie.html', searchNo = searchNo)                     
    except NameError:
        print("Something else went wrong")
    return render_template('movie.html', search_list = search_list, url_img_base = url_img_base)

@app.route('/detail/<id>', methods=['GET','POST'])
def detail(id):  
    # Obtiene los detalles y trailer de la pelicula seleccionada  
    try:
        #if method.request == 'GET':        
        search_details = movie.details(id)               
        year = '{:.4}'.format(search_details.release_date) # se obtiene el a;o
        if search_details.videos['results'] != [] or "":
            trailer = search_details.videos['results'][0].key # se obtiene el trailer
            genre_list = get_genres(id) # funcion para generar el genero           
        else:            
            return render_template('no_found.html', searchNo = 'Trailer No Found', found = search_details, year = year, genres = genre_list), 404       
    except NameError:
        return render_template('no_found.html', searchNo = 'Trailer No Found', found = search_details, year = year), 404        
    return render_template('detail.html', trailer = trailer, genres = genre_list, searchs_details = search_details, year = year)


@app.route('/discover', methods=['GET', 'POST'])
def discover_new():
    # obtiene una serie de recomendaciones basadas en criterios
    try:
        """ movie = discover.discover_movies({
            'year': '2020',
            'with_genres': '28'
        }) """
        # What movies are in theatres?    
        movie = discover.discover_movies({
            'primary_release_date.gte': '2021-01-20',
            'primary_release_date.lte': '2021-02-24'
        })

        #Year and genre
        """ movie = discover.discover_movies({
            'year': '2018',
            'with_genres': '28' #Action
        }) """
        # Best Drama
        """ movie = discover.discover_movies({
            'with_genres': '28',
            'sort_by': 'vote_average.desc',
            'vote_count.gte': '10' 
        }) """
        # What are the most popular movies?
        """ movie = discover.discover_movies({
            'sort_by': 'popularity.desc'
        }) """

        # What are the most popular kids movies?
        """ movie = discover.discover_movies({
            'certification_country': 'US',
            'certification.lte': 'G',
            'sort_by': 'popularity.asc'
        }) """
        # desde el search obtiene las peliculas segun el a;o
        search_list = []        
        if request.method == 'POST':
            year_movie = request.form['Title']            
            if len(year_movie) > 0:
                search_list = discover.discover_movies({'year' : year_movie}) 
                return render_template('discover.html', discover_list = search_list, url_img_base = url_img_base)                      
            else:
                searchNo = 'No Search'
                return render_template('discover.html', searchNo = searchNo)
    except NameError:
        print("Something else went wrong")
    return render_template('discover.html', discover_list = movie, url_img_base = url_img_base)

    
@app.route('/recommendation/<id>')
def recommendation_movie(id):  
    # recomendaciones generadas a partir de la seleccion de una pelicula  
    
    searchs_details = movie.details(id)
    recommendat = movie.recommendations(id)          
    
    return render_template('recommendation.html', reco = recommendat, searchs_details = searchs_details, url_img_base = url_img_base)

@app.route('/tvshow', methods=['GET', 'POST'])
def tvshow(): 
    '''
    obtiene lista de series de tv basadas en el criterio de busqueda
    '''
    if request.method == 'GET':
            return trendTv()
    show = []
    if request.method == 'POST':
        tv_show = request.form['tv_show']
        if len(tv_show) != 0:      
            show = tv.search(tv_show)
        else:
            searchNo = 'No Search'
            return render_template('tvshow.html', searchNo = searchNo)

    return render_template('tvshow.html', show = show, url_img_base = url_img_base)

@app.route('/tvseason/<id>')
def tvseason(id):
    # obtiene las temporadas asociadas a una serie-tv
    tv_details = tv.details(id)    
    
    return render_template('tvseason.html', tv_details = tv_details, url_img_base = url_img_base)

@app.route('/tvepisode/<id>/<season_number>')
def tv_episode(id, season_number):
    # obtiene los episodios de una temporada de la serie seleccionada

    show_season = season.details(id, season_number)    
    
    return render_template('tvepisode.html', show_season = show_season, url_img_base = url_img_base)


if __name__ == "__main__":
    app.run(debug=True)

