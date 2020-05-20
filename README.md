# SQL and iTunes API

![](https://apple-resources.s3.amazonaws.com/medusa/production/images/5e28cacfd01ec800014020f4/en-us-large@1x.png)

This morning we will be querying data from the [Chinook Database](https://www.sqlitetutorial.net/sqlite-sample-database/) and collecting new information with the [iTunes API](https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/)!


```python
# SQL Connection and Querying
import sqlite3

# Data manipulation
import pandas as pd

# API Connection
import requests

#for tests
from test_background import test_obj_dict, run_test_dict, pkl_dump, run_test
```

The database in stores within the ```data``` folder of this repo as ```chinook.db```


<u>In the cell below:</u>
1. Open up a connection to ```chinook.db``` and store that connection as ```conn```


```python
conn = sqlite3.connect('chinook.db')
```

Let's create a function called ```sql_df``` that returns a dataframe of a SQL query.

<u>In the cell below:</u>
1. Define a function called ```sql_df``` that takes in two parameters ```query```, and ```connection```.
2. Return a dataframe from the function using [pd.read_sql](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_sql.html)


```python
def sql_df(query, connection):
    return pd.read_sql(query, connection)
```

<img src=schema.png width=700/>

**Above is the schema for the Chinook Database.** 

For this warmup, we will be focusing on the ```tracks```, ```albums```, and ```artists``` tables.

We'll start with something simple for our first SQL query. 

<u>In the cell below:</u>
1. Write a SQL query to collect all columns from the ```tracks``` table 
2. ```LIMIT``` the query to only return two records from the table.
3. Run the query through the ```sql_df``` function and save the results as the variable ```first_query```.


```python
QUERY = """SELECT * FROM tracks LIMIT 2;"""
first_query = sql_df(QUERY, conn)

#used for tests 
# pkl_dump([
#     (first_query,
#     'first_query'
#     )
# ])
```

Run the cell below to see if your query returned the correct data!

**Ok ok**

Let's do a more complex query. 

<u>In the cell below:</u>
1. Write a sql query that selects 
    - The ```Name``` column from the ```tracks``` table
        - Alias this column as ```Song```
    - The ```Title``` column from the ```albums``` table
        - Alias this column as ```Album```
    - The ```Name``` column from the ```artists``` table
        - Alias this column as ```Artist```
    - Use the ```WHERE``` command to only return results where ```Artist = 'U2'```
    - ```LIMIT``` the results to 15 observations.
        
**Hint:** This will require you to first join the ```tracks``` and ```albums``` tables, and then join the ```artists``` table.

We'll save the results of this query to the variable `df`


```python

QUERY = """SELECT tracks.Name as Song,  
                  albums.Title as Album,
                  artists.Name as Artist
            FROM tracks
            JOIN albums
            USING(AlbumId)
            JOIN artists
            USING(ArtistId)
            WHERE Artist = 'U2'
            LIMIT 15"""

df = sql_df(QUERY, conn)
df.head()

#used for tests
# pkl_dump([
#     (df,
#     'query_to_df'
#     )
# ])
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Song</th>
      <th>Album</th>
      <th>Artist</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>Zoo Station</td>
      <td>Achtung Baby</td>
      <td>U2</td>
    </tr>
    <tr>
      <td>1</td>
      <td>Even Better Than The Real Thing</td>
      <td>Achtung Baby</td>
      <td>U2</td>
    </tr>
    <tr>
      <td>2</td>
      <td>One</td>
      <td>Achtung Baby</td>
      <td>U2</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Until The End Of The World</td>
      <td>Achtung Baby</td>
      <td>U2</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Who's Gonna Ride Your Wild Horses</td>
      <td>Achtung Baby</td>
      <td>U2</td>
    </tr>
  </tbody>
</table>
</div>



Run the cell below to see if you returned the correct results!

<center><u>Our df variable is made up of a table with three columns</u></center>

|Song|Album|Artist|
|----|-----|------|
|Name of<br>song|Name of<br>album|Name of<br>artist|

-----

**Let's collect the release date of each song using the [iTunes Search API](https://affiliate.itunes.apple.com/resources/documentation/itunes-store-web-service-search-api/) and add it as a column to our dataframe**

To do this, we will use three paramaters. ```term```, ```entity```, and ```limit```.

**term**
>The iTunes API interprets this paramater the same way it iterprets a search term you would manually type when searching for songs on iTunes

**entity**
>This parameter is a filter for our search. We can filter our search to only return albums, music videos, etc. For this warmup we will be filtering our search to only return songs

**limit**
>The limit parameter determines how many search results are returned. The minimum is 50, the maximum is 200. For this warmup, we will set this to 200

**The iTunes API only allows 20 requests per minute.**

We could search each song individually with

```
req_string = 'https://itunes.apple.com/search?term={}&entity=song&limit=200'.format(song)
requests.get(req_string).json()

```

But what if our code malfunctions? We risk sending too many requests, at which point the iTunes API will refuse our requests! We don't want that.

*Fortunately for us*, we can collect the data we need with a single request.

Instead of using the name of the song as our search term, we will use the name of the artist and keep our entity parameter as ```song``` so the results return individual songs created by the artist.

<u>In the cell below:</u>
1. Replace ```None``` with the variable needed to search the iTunes API for songs by the artist ```U2```


```python
req_string = 'https://itunes.apple.com/search?term={}&entity=song&limit=200'.format('U2')

#used for tests
# pkl_dump([
#     (req_string,
#      'req_string'
#     )
# ])
```

Run the cell below to see if your ```req_string``` variable is correct!

Now that we have our req_string, we can send our request to the API using the ```requests``` library.


```python
req = requests.get(req_string).json()
req.keys()
```




    dict_keys(['resultCount', 'results'])



The data returned from the API is formatted as a ```json``` which for most intents and purposes is just a dictionary.

The information we want from this json is found with the ```'results'``` key.


```python
api_data = req['results']
type(api_data)
```




    list



<u>Ok ok! Now that we have our data from the api,</u> **Here's what we need to do:**

![](https://media.giphy.com/media/LpkBAUDg53FI8xLmg1/giphy.gif)

1. Create an empty list called ```dates```.
2. Loop over the rows of our dataframe
2. Collect the song name and artist name from the dataframe row.
3. Loop over each result in ```api_data```.
4. Check if:
    - The song in our dataframe row is equal to ```result['trackName']``` 
    - The artist in our dataframe row is equal to  ```result['artistName']```
5. If the song and artist match: 
    - Set the variable ```release_date``` to ```result['releaseDate']``` 
    - Append ```release_date``` to the ```dates``` list 
    - ```break``` out of the nested for loop.
6. If the song and artist do not match:
    - Set ```release_date``` to ```None```
7. If the nested for loop completes and ```release_date``` still equals ```None```:
    - Append ```None``` to the ```dates``` list.
8. Add a ```release_date``` column to ```df``` using the ```dates``` list.


```python
dates = []

for idx, row in df.iterrows():
    song = row.Song
    artist = row.Artist
    
    for result in api_data:
        if result['trackName'] == song and result['artistName'] == artist:
            release_date = result['releaseDate']
            dates.append(release_date)
            break
        
        else:
            release_date = None
            
    if not release_date:
        dates.append(release_date)
            
df['release_date'] = dates 
df['release_date']
##used for tests
# pkl_dump([
#     (
#         df,
#         'release_date'
#     )
# ])
```




    0     1988-11-18T12:00:00Z
    1                     None
    2     1988-11-18T12:00:00Z
    3                     None
    4     1988-11-18T12:00:00Z
    5     1988-11-18T12:00:00Z
    6     1991-10-21T12:00:00Z
    7     1988-11-18T12:00:00Z
    8                     None
    9                     None
    10    1988-11-18T12:00:00Z
    11    1988-11-18T12:00:00Z
    12    2000-10-01T12:00:00Z
    13                    None
    14                    None
    Name: release_date, dtype: object



Let's take a look at the results


```python
# Run this cell as is
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Song</th>
      <th>Album</th>
      <th>Artist</th>
      <th>release_date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>Zoo Station</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>1</td>
      <td>Even Better Than The Real Thing</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>None</td>
    </tr>
    <tr>
      <td>2</td>
      <td>One</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Until The End Of The World</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>None</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Who's Gonna Ride Your Wild Horses</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>5</td>
      <td>So Cruel</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>6</td>
      <td>The Fly</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1991-10-21T12:00:00Z</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Mysterious Ways</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Tryin' To Throw Your Arms Around The World</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>None</td>
    </tr>
    <tr>
      <td>9</td>
      <td>Ultraviolet (Light My Way)</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>None</td>
    </tr>
    <tr>
      <td>10</td>
      <td>Acrobat</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>11</td>
      <td>Love Is Blindness</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>12</td>
      <td>Beautiful Day</td>
      <td>All That You Can't Leave Behind</td>
      <td>U2</td>
      <td>2000-10-01T12:00:00Z</td>
    </tr>
    <tr>
      <td>13</td>
      <td>Stuck In A Moment You Can't Get Out Of</td>
      <td>All That You Can't Leave Behind</td>
      <td>U2</td>
      <td>None</td>
    </tr>
    <tr>
      <td>14</td>
      <td>Elevation</td>
      <td>All That You Can't Leave Behind</td>
      <td>U2</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



Run the cell below to check if you collected the correct release dates!

It looks like there are several ```None```'s in our ```release_date``` column. *And there is a reason for this.*

The word ```the``` is capitalized in our Chinook database but is lowercased by the iTunes API.

Run the cell below to see why this is a problem.


```python
'Even Better Than The Real Thing' == 'Even Better Than the Real Thing'
```




    False



Yikes! So how do we solve this? 

We can solve this by  ```lowering``` all strings when we compare them so no matter what, the strings are cased exactly the same.


```python
'Even Better Than The Real Thing'.lower() == 'Even Better Than the Real Thing'.lower()
```




    True



Copy and paste your code from above in the cell below, except this time lower all string values.


```python
dates = []

for idx, row in df.iterrows():
    song = row.Song.lower()
    artist = row.Artist.lower()
    
    for result in api_data:
        if result['trackName'].lower() == song and result['artistName'].lower() == artist:
            release_date = result['releaseDate']
            dates.append(release_date)
            break
        
        else:
            release_date = None
            
    if not release_date:
        dates.append(release_date)
            
df['release_date'] = dates 

df['release_date']

#used for tests
# pkl_dump([
#     (
#         df,
#         'string_manip'
#     )
    
# ])
```




    0     1988-11-18T12:00:00Z
    1     1988-11-18T12:00:00Z
    2     1988-11-18T12:00:00Z
    3     1988-11-18T12:00:00Z
    4     1988-11-18T12:00:00Z
    5     1988-11-18T12:00:00Z
    6     1991-10-21T12:00:00Z
    7     1988-11-18T12:00:00Z
    8     1988-11-18T12:00:00Z
    9                     None
    10    1988-11-18T12:00:00Z
    11    1988-11-18T12:00:00Z
    12    2000-10-01T12:00:00Z
    13    2000-10-30T12:00:00Z
    14                    None
    Name: release_date, dtype: object




```python
# Run this cell as is
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Song</th>
      <th>Album</th>
      <th>Artist</th>
      <th>release_date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>Zoo Station</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>1</td>
      <td>Even Better Than The Real Thing</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>2</td>
      <td>One</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Until The End Of The World</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Who's Gonna Ride Your Wild Horses</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>5</td>
      <td>So Cruel</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>6</td>
      <td>The Fly</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1991-10-21T12:00:00Z</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Mysterious Ways</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Tryin' To Throw Your Arms Around The World</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>9</td>
      <td>Ultraviolet (Light My Way)</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>None</td>
    </tr>
    <tr>
      <td>10</td>
      <td>Acrobat</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>11</td>
      <td>Love Is Blindness</td>
      <td>Achtung Baby</td>
      <td>U2</td>
      <td>1988-11-18T12:00:00Z</td>
    </tr>
    <tr>
      <td>12</td>
      <td>Beautiful Day</td>
      <td>All That You Can't Leave Behind</td>
      <td>U2</td>
      <td>2000-10-01T12:00:00Z</td>
    </tr>
    <tr>
      <td>13</td>
      <td>Stuck In A Moment You Can't Get Out Of</td>
      <td>All That You Can't Leave Behind</td>
      <td>U2</td>
      <td>2000-10-30T12:00:00Z</td>
    </tr>
    <tr>
      <td>14</td>
      <td>Elevation</td>
      <td>All That You Can't Leave Behind</td>
      <td>U2</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



Run the cell below to see if you were successful!
