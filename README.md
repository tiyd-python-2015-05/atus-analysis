Summary:
I looked at many way people spend time against their age. Take a look at the 
ipython notebook for the calculations. Here are a few summaries:

-sleep vs age: upright parabola, centered around 50 years. 50 year olds on 
average get the least amount of sleep. Going both directions, older and younger, people tend to get more sleep.

-religious activity vs age: roughly slow steady increase until a big spike around 60-80 year olds

-socializing vs aged: heightened around 20 year olds, and a noticable decrease into 30's. 
slow ups and downs from there

-civic obligations vs age: sharp spike around 60-70 year olds

NOTE:This is by no means comprehensive. The data that was used has many facets, and is spread out in different ways, making it difficult to aggregate all of it to a single statistic.
Something else to note about the data is there is  no "multi-tasking", i.e. if somebody is grooming they cannot be socializing at the same time.



# American Time Use Analysis

## Description

Use the U.S. Department of Labor's data on Americans' time use for research and analysis.

## Objectives

### Learning Objectives

After completing this assignment, you should understand:

* How to use public data for analysis
* How to translate data from CSVs to relational databases
* How to publish your own data analysis as a notebook

### Performance Objectives

After completing this assignment, you should be able to:

* Use pandas to parse and analyze data
* Use matplotlib to chart data
* Clean data

## Details

### Deliverables

* A Git repo called atus-analysis containing at least:
  * `README.md` file explaining how to run your project
  * a `requirements.txt` file
  * an IPython notebook with your analysis
  * a suite of tests for your project

### Requirements  

* Passing unit tests
* No PEP8 or Pyflakes warnings or errors

## Normal Mode

The U.S. Bureau of Labor Statistics publishes yearly data about Americans' use
of their time: [American Time Use Survey](http://www.bls.gov/tus/home.htm#data).
This data is used to find out information like how many hours the average person
spends per day doing household activities. You can see
[the 2013 survey results](http://www.bls.gov/news.release/atus.nr0.htm)
for more examples. You should use these results to double-check your logic as well.

You will download the 2013 files and use these to do analysis. The questions you are trying to answer are up to you, but they
should at least:

* Compare different populations (people with children and people without, people of differing age groups, men and women, or other groupings)
* Answer macro-level questions and micro-level questions (for example, the amount of leisure for the macro-level, the types of things people do for leisure for the micro-level)

Your final analysis should be in the form of an IPython Notebook with both
narrative analysis and supporting charts. Your supporting code should be in
normal Python files.



## Additional Resources

* [How to use ATUS microdata files](http://www.bls.gov/tus/howto.htm)
* [ATUS Coding Lexicon - you will need this](http://www.bls.gov/tus/lexicons.htm)
