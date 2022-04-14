# ReadMe
----
**General Assembly Project 3**
AP Data Collection and Classification Model Analysis of popular Reddit Threads.

by Chris Durso

# Background
----

**Scenario**
You're fresh out of your Data Science bootcamp and looking to break through in the world of freelance data journalism. Nate Silver and co. at FiveThirtyEight have agreed to hear your pitch for a story in two weeks!

Your piece is going to be on how to create a Reddit post that will get the most engagement from Reddit users. Because this is FiveThirtyEight, you're going to have to get data and analyze it in order to make a compelling narrative.

**Problem Statement**
*What characteristics of a post on Reddit are most predictive of the overall interaction on a thread (as measured by number of comments)?*

In order to acheive this a number of models will be developed startign with KNN and Random Forests with a target of Number of Posts Greater than the Median Posts and eventually incorporating NLP into the analysis.

In order to ensure the model is successful it will be graded against the Baseline Score (prabaility that a thread chosen at random is over the median score)

Once completed I will be pitching a blog post about how to creat a Reddit post that will get the most engagement from Reddit users. FiveThirtyEight is known for their incorporation of statistics in their reporting so in order to create a compelling narrative I will need to ensure all of my analysis is top notch.


## Workbook Structure
---

### Notebooks
----
 - 1 - Pull Threads
 - 2 - Create DF
 - 3 - EDA & Modelling
 - 4 - NLP
 
### data
----
 - thread_df - initial dataframe
 - thread_df-BACKUPDATA.csv - Backup data in case the original is lost
>#### assets
> - Images
>>#### json
>>>#### [2021-12-26] - [2022-01-07]
>>> - json files in name format: YYYY-MM-DD-HH

### auth
----
password_directory.ini

# Data Collection
----
Data was collected from r/popular using the Reddit API from 12/26 to 1/7 every 4 hours on the intervals of 00:00, 04:00, 08:00, 12:00, 16:00 and 20:00.

Data was collected and stored in raw json format from the API so that any features needed would be accessible if needed. In the preprocessing step (incorreclty labelled Create DataFrame) json data was read in, formatted into a pandas dataframe and cleaned of all NA's.

Functions within both the PullThreads and CreateDataFrame were created with the intention of avoiding hard coding to specific features for easy modifications if necessary

# EDA and Feature Engineering
----

## EDA
----
### Correlation Heatmap
Starting with a Correlation Heatmap to determine which features are worth focussing on.

These two are the main highlights and most likely to improve the model
- `time_on_reddit`
- `subreddit count`

The following are also noteworthy
- `num_comments` (`above_median` is derived from it and can't be used in modelling)
- `subreddit_subscribers` 
- `num_crossposts`
- `text_thread`

![](https://git.generalassemb.ly/ambisinisterr/project_3/blob/master/data/assets/heatmap.png)

### Time on Reddit
There are two aspects to this which need to be considered.

1. The threads which are extremely popular in short times such as the two at the 20,000 second mark are technically outliers but in this case are the threads which we care about the most. These are explosive and directly popular.
2. Threads which are on reddit longer will naturally grow in post counts. On one hand this makes them less relevant but on the other hand the fact they have remained on r/popular over time means they have a form of endurance. These threads threads have endured and have features which keep them indirectly popular.

Both types of interactions should be featured and explained in the model.

![](https://git.generalassemb.ly/ambisinisterr/project_3/blob/master/data/assets/timeonreddit.png)

### Dataset Appearances to Number of Comments
Despite this being a strong feature is is rather noisy.

It isn't really feasible to see the overall trend in the data, though, so a second rendering was created to plot the numbers of median comments by subreddit count at each quartile and see if there is an overall trend.

![](https://git.generalassemb.ly/ambisinisterr/project_3/blob/master/data/assets/subreeddit_count1.png)
![](https://git.generalassemb.ly/ambisinisterr/project_3/blob/master/data/assets/subreddit_count2.png)

### Parent Whitelist Status
This was not the one of the strongest correlations in the data but as marketing plays a huge role for Reddit there needed to be some exploration into how ad approval affects whether the post will get comments.

As it turns out there is still relevant information especially for a classification model. There are two clear categories on display in this visualization between allowing all ads and not allowing ads and the model should be able to utilize this data.

![](https://git.generalassemb.ly/ambisinisterr/project_3/blob/master/data/assets/whitelist_status.png)

### Number of Crossposts
This visualization depicts several classes being formed between 0-1M Subscribers, 1-2M Subscribers and around 3 and 4M subscribers. The green line shows the median post counts at given ranges of subscribers.

I also added in an additional hue of whether the thread has text or not as that 

KNN and Random Forest Classifiers will use these groupings to make more accurate predictions.

![](https://git.generalassemb.ly/ambisinisterr/project_3/blob/master/data/assets/crossposts.png)

# KNN
----
Based on EDA there shouldn't be any issues designing classification models witht he data I collected.
### Baseline Score
If a random thread was drawn from a hat we could expect the thread to be above the median thread count 50.22% of the time.

### KNN Model 1 (Simple)
Default Model with just pulled information required for project. No feature engineering.

With a score of 68.92% +- 0.30% this is a signifigant improvement over the baseline score of 50.22% with just the basic setup.

----

Simple Score: 68.92% +- 0.30%


### KNN Model 2 (Includes Gridsearch and Feature Engineering)
Added a GridSearch and engineered features.

I opted to keep the K Values low. Ideally the K Value of this size of dataset should be 244 (square root of N) but this is just far too computationally intensive for this task. KNN is a great classifier but falls off on larger and more complex datasets.

We can see this reflected by only getting a modest improvement despite adding additional criteria which should help the classification metrics.

----

Simple Score: 68.92% +- 0.30%

GSCV Score: 75.18% +- 0.27%


# Random Forest
----
Surprisingly the Random Forest actually only showed a modest improvement over the KNN model.

Random Forest should be a superior model but without further exploration it is hard to prove which is. The random Forrest is less prone to overfitting so despite scoring similarly the Random Forest model is likely be far superior in practical applications.

----

RF GSCV Score: 76.97% +- 0.35%

# NLP
----
Note a lot of my rsearch and code was derived from the work Lily Wu blogged about.

https://towardsdatascience.com/clustering-product-names-with-python-part-1-f9418f8705c8

## Preprocessing
----
There was an issue with during vectoriztion where there was simply too much information in the ~59,250 threads and it resulted in the following memory errors when applying it to a pandas dataframe:

`MemoryError: Unable to allocate 18.2 GiB for an array with shape (41292, 59250) and data type int64`

This could be reduced or outright solved by improving stop words. Unfortunately due to time constraints the best option is to simply focus on the threads with the most interactions. By selecting only threads that have over 200 comments the dataframe has been reduced to 11,117.

*Side Note: Spacy has a pipline method which would increase the tokenization process immensely.*

## Vectorize
----
### Bag of Words
Back of words is the most basic NLP model. I don't expect to use it but it can give us insights into the TF-IDF model or be used to compare results.

### TF-IDF
TF-IDF is an NLP that performs similarly to PCA. It uses vector inversions to logrithmically remove results from the data. This results in a stronger signal/less noise in the model.

### TF-IDF (n-gram level)
This final model is TF-IDF with an n-gram evaluation to determine words which are within sentences together. This did not perform well in the LDA section based on thread titles but I suspect it would work well if applied to thread text.

### LDA
----
Topic Classification!

This is a really basic version of this amazing model but it is trained using the TF-IDF model. The TF-IDF with n-grams did not seem to have enough text to build a successful model within LDA.

Note the code to  code is directly from:

https://scikit-learn.org/stable/auto_examples/applications/plot_topics_extraction_with_nmf_lda.html

![](https://git.generalassemb.ly/ambisinisterr/project_3/blob/master/data/assets/topics.png)

# Conclusions
----
### Without NLP
----
Based in the information gathered from Reddit the features which are most predictive of a threads interaction, based on the number of comments, are:

| Feature | Effect |
| ------- | ------ |
| subreddit_subscribers | As subscriptions increase, p of above_median increases |
| num_crossposts | As crossposts increase, p of above_median increases |
| time_on_reddit | As time on r/popular increases, p of above_median increases |
| text_thread | If text_thread, p of above_median inccreases (modest effect) |
| subreddit_count | As subreddit_count increases, p of above_median increases |

In order to develop a thread that increases interactions (as measured by number of comments) threads should:

- be posted on subreddits with high subscriptions
- be cross posted to multiple subreddits
- be a topic with explosive popularity or endure for several days with modest popularity
- be posted on one of the subreddits that consistently have high post counts

Examples of the last type are:

- r/memes - 246 appearances
- r/Superstonk - 182 appearances
- r/HolUp - 180 appearances
- r/shitposting - 180 appearances

### NLP Conclusions
----
Using a compination of TF-IDF and LDA I was able to determine 30 topics categorizations.

 - Topic 2 appears to be discussing sports
 - Topic 3 appears to be discussing the holiday season
 - Topic 4 is discussing the loss of Betty White
 - Elon Musk also made an appearance in Topic 10
 - I am not sure I want to know more about Topic 29.

Using LDA I was able to determine the trending topics but there is more fine tuning to do to better determine the Topics of these more nebulous words. Even with this admittedly crude model we can see trends that definitely occurred in the last few weeks appearing such as the tragic death of Betty White just before her 100th birthday.

While the model could be greatly refined with additional stopwords the fact such diverse topics are successfully being categorized lends credence to the model's predicative capabilities.
