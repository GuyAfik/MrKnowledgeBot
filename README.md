# MrKnowledgeBot

MrKnowledgeBot is a telegram bot that provides information about movies/tv-shows.
MrKnowledgeBot supports some basic concepts of CLI use in order to track easily which arguments were provided.

The bot is hosted on the cloud (heroku) so you can feel free to access it through this URL:

```
https://t.me/mr_knowledge_bot
```

## Demo

### find_movies_by_name


https://user-images.githubusercontent.com/53861351/194547868-5c303d10-3f77-4897-aa4a-88b12f5974d6.mp4

### find_tv_shows_by_name

https://user-images.githubusercontent.com/53861351/194550438-b7bdd44a-9b3f-4f86-a88a-efdee3bf97a2.mp4


## Supported commands
- */help* - List the commands supported by the MrKnowledgeBot.
- */find_movies_by_name* - Allows you to find movies by name, query for movie details and trailers if those exist.
- */discover_movies* - Allows you to find movies by several options such as rating/popularity/release-date/genres and more. query for movie details and trailer if exist.
- */find_tv_shows_by_name* - Allows you to find tv-shows by name.
- */discover_movies* - Allows you to find movies by several options such as rating/popularity/release-date/genres and more.
- */get_movie_genres* - Returns a list of movie genres that the bot supports.
- */get_tv_shows_genres* - Returns a list of tv-shows genres that the bot supports.

### help command execution
```
Hello Guy Afik! Here are the available conversations 😎

/help: List the conversations supported by the MrKnowledgeBot
/find_movies_by_name: Allows you to find movies by name.
/discover_movies: Allows you to discover movies by several options.
/find_tv_shows_by_name: Allows you to find tv-shows by name.
/discover_tv_shows: Allows you to discover TV-shows by several options.
/get_movie_genres: Retrieves the available movies genres.
/get_tv_shows_genres: Retrieves the available TV-shows genres.

For more information please refer to https://github.com/GuyAfik/MrKnowledgeBot/blob/master/README.md
```

### find_movies_by_name command usage
```
Usage:
/find_movies_by_name [ARGS]

Description:
Allows you to find movies by name.

Arguments:
  —name, —n  STR  The movie name to search for (can be substrings or partial movie names)
  —limit, —l  INT  The maximum amount of movies to return, maximum is 100. (default=50)
  —sort-by, —s  STR  Sort by one of the following: popularity/release_date/rating. (default=popularity) (allowed-values=popularity,release_date,rating)

Examples:
1) /find_movies_by_name -n "game of thrones"
2) /find_movies_by_name -n "game of thrones" -l "20"
3) /find_movies_by_name -n "game of thrones" -l "10" -s "release_date"
```

### discover_movies command usage
```
Usage:
/discover_movies [FLAGS] [ARGS]

Description:
Allows you to discover movies by several options.

Flags:
  —not_released, —nr  Bring movies that were still not released.

Arguments:
  —limit, —l  INT  The maximum amount of movies to return, maximum is 100. (default=50)
  —sort-by, —s  STR  Sort by one of the allowed values (default=popularity) (allowed-values=popularity,release_date,rating)
  —before_date, —bd  STR  Movies that were released before the specified date in the form of a date. "year-month-day"
  —after_date, —ad  STR  Movies that were released after the specified date in the form of a date. "year-month-day"
  —with_genres, —wg  LIST  Comma-separated list of movies genres to retrieve. Can be retrieved from the get_movies_genres command.
  —without_genres, —wog  LIST  Comma-separated list of movies genres to not retrieve. Can be retrieved from the get_movies_genres command.
  —before_runtime, —br  INT  Movies that their duration is no longer than the specific runtime. (minutes)
  —after_runtime, —ar  INT  Movies that their duration is longer than the specific runtime. (minutes)

Examples:
1) /discover_movies -l "80"
2) /discover_movies -s "popularity"
3) /discover_movies -bd "2014-09-13"
4) /discover_movies -ad "2014-09-13"
5) /discover_movies -wg "Science Fiction,Fantasy"
6) /discover_movies -wog "Science Fiction,Fantasy"
7) /discover_movies -br "120"
8) /discover_movies -ar "120"
9) /discover_movies —not_released
```

### find_tv_shows_by_name command usage
```
Usage:
/find_tv_shows_by_name [ARGS]

Description:
Allows you to find tv-shows by name.

Arguments:
  —name, —n  STR  The tv-show name to search for (can be substrings or partial tv-show names)
  —limit, —l  INT  The maximum amount of tv-shows to return, maximum is 100. (default=50)
  —sort-by, —s  STR  Sort by one of the following: popularity/release_date/rating. (default=popularity) (allowed-values=popularity,release_date,rating)

Examples:
1) /find_tv_shows_by_name -n "game of thrones"
2) /find_tv_shows_by_name -n "game of thrones" -l "20"
3) /find_tv_shows_by_name -n "game of thrones" -l "10" -s "release_date"
```

### discover_tv_shows command usage
```
Usage:
/discover_tv_shows [FLAGS] [ARGS]

Description:
Allows you to discover TV-shows by several options.

Flags:
  —not_released, —nr  Bring movies that were still not released.

Arguments:
  —limit, —l  INT  The maximum amount of tv-shows to return, maximum is 100. (default=50)
  —sort-by, —s  STR  Sort by one of the allowed values (default=popularity) (allowed-values=popularity,first_air_date,rating)
  —before_date, —bd  STR  TV-shows that were released before the specified date in the form of a date. "year-month-day"
  —after_date, —ad  STR  TV-shows that were released after the specified date in the form of a date. "year-month-day"
  —with_genres, —wg  LIST  TV-shows that are one of the genres that the get_tv_shows_genres command returns
  —without_genres, —wog  LIST  TV-shows that are not one of the genres that the get_tv_shows_genres returns.
  —before_runtime, —br  INT  Filter and only include TV shows with an episode runtime that is less than or equal to a value. (minutes)
  —after_runtime, —ar  INT  Filter and only include TV shows with an episode runtime that is greater than or equal to a value. (minutes)
  —with_status, —ws  STR  Filter TV shows by their status. (allowed-values=Returning Series,Planned,In Production,Ended,Cancelled,Pilot)

Examples:
1) /discover_tv_shows -l "80"
2) /discover_tv_shows -s "popularity"
3) /discover_tv_shows -bd "2014-09-13"
4) /discover_tv_shows -ad "2014-09-13"
5) /discover_tv_shows -wg "Science Fiction"
6) /discover_tv_shows -wog "Science Fiction"
7) /discover_tv_shows -br "120"
8) /discover_tv_shows -ar "120"
9) /discover_tv_shows -ws "Planned"
10) /discover_tv_shows —not_released
```

### get_movie_genres command usage
```
Usage:
/get_movie_genres

Description:
Retrieves the available movies genres.
```

### get_tv_shows_genres command usage
```
Usage:
/get_tv_shows_genres

Description:
Retrieves the available TV-shows genres.
```




