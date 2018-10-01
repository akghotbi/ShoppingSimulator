# Simulating Virtual Shopping Environment

## Abstract
In a shopping scenario, regardless of location being online or at a  physical store, a client will be presented with an assortment of available products on the shelves at the store. Depending on her preferences, she then selects one or more of the products in the category. After she consumes all she bought, she comes back to fill her pantry again. 

Simulating such behavior is at the core of model validation for many marketing research companies. This, for example, enables a researcher to assume different behavioral models, generate consumer data accordingly, and assess how biased her current regression or classification models are for each assumed shopping behavior.

The aim of this project is to introduce a simple simulator which mimics assortment changes from one shopping trip to another as well as choices consumers make given the products available to them at each trip.  

## I. Design assumptions
### I.1 User specific assumptions
The code provided assumes there are *G* groups of like-minded shoppers. A user *u* comes from one of these groups. The probability that she belongs to group *g* is *p_g*. Moreover, given her group, her preferences are drawn from a Gaussian distribution. These values (also called utilities) are used in a user specific logit model to generate choice probability vector for all products. In short, the following generative process holds:

![group_draw](https://latex.codecogs.com/gif.latex?g_u%3A%20Mult%28p_1%2C%20%5Cldots%2C%20p_G%3B1%29)

![utility_draw](https://latex.codecogs.com/gif.latex?%5Cbeta_u%7Cg_u%3A%5C%20Gaussian%28%5Cmu_%7Bg%2Cu%7D%2C%20%5CSigma_%7Bg%2Cu%7D%29%2C%5C%20%5Cbeta_u%5Cin%20%5Cmathbb%7BR%7D%5E%7BnumItems%7D)

![choice_prob](https://latex.codecogs.com/gif.latex?p%28select%5C%20item_j%7Cassortment%5C%20A%2C%20%5Cbeta_u%29%20%3D%20%5Cfrac%7Be%5E%7B%5Cbeta_%7Bu%2Cj%7D%7D%7D%7B%5Csum_%7Bj%5Cin%20A%7D%20e%5E%7B%5Cbeta_%7Bu%2Cj%7D%7D%7D)

Most of this functionality is coded in ``src.dataset.user`` module.

### I.2 Design of experiment (DoE)
The proper way of sampling assortments is via full or partial factorial designs which are balanced and orthogonal. Balanced design ensures that each user sees each item equally likely across her shopping trips, whereas, orthogonality ensures flat co-occurrences.

For simplicity, instead, a simple algorithm with receding quotas is used which ensures excellent balance and appropriate co-occurrences. This easy to understand algorithm can be found in ``src.dataset.doe`` module.

## II. How to run and test:
To run this project, please clone the repository first. It is assumed that you have ``virtualenv`` installed.

1- Navigate to the project root directory and create a new virtual environment by typing 
```angular2html
virtualenv --no-site-packages -p <YOUR_PYTHON_PATH> ShoppingSimulator

``` 
Activate this environment before going to the next step.

2- Install the required packages via
```angular2html
pip install -r requirements.txt
```

3- To run the code using provided inputs and generate output, please run
```angular2html
python . -i input_data -o results -ng 3 -ni 12
```
Note that you can change the contents of csv files and do more experiments. However, the number of groups and dimensions of mean and cov of Gaussians should be compatible.

4- I have also written a small unit test for this code. It uses a separate set of files to avoid interference with regular runs. To run test, type the followings in your shell:
```angular2html
python -m unittest test/test_shopping_simulator.py
```

## III. Code structure
### III.1 General
The project folder is ``ShoppingSimulator``. The main entry to the code is ``ShoppingSimulator/__main__.py``. 

The project consists of a master module ``src.dataset`` with class ``DatasetBuilder`` and encompasses the following three sub-modules:

1- ``src.dataset.doe``: Contains ``dataset_builder.py`` and class ``DoEBuilder`` for simple assortment sampling.

2- ``src.user``: Contains ``user_builder.py`` and class ``UserBuilder`` for generating artificial users/shoppers.

3- ``src.parsers``: Contains ``distribution_parser.py`` and class ``DistributionParser`` for parsing information on Gaussian distributions provided by csv input files.

### III.2 Inputs and outputs: 
#### Commandline arguments
The inputs are provided via commandline arguments. Detailed description of commandline arguments is as follows:
```angular2html
Mandatory Inputs:
    -i:     Input directory  (relative to project root)
    -o:     Output directory (relative to project root)
    -ng:    Number of canonical groups of like minded shoppers
    -ni:    Number of total items in the category

Optional Inputs:
    -gdf:   csv file name in input dir including the group specific Gaussian distributions
            Default: 'user_group_distributions.csv'
    -gpf:   csv file name in input dir including membership probability for each group
            Default: 'user_group_probabilities.csv'
    -nu:    Number of users to be simulated
            Default: 450
    -nt:    Number of shopping trips per user
            Default: 18
    -ss:    The shelf size at store. In each trip, a random number of items are selected and
            will be available on store shelf.
            Default: 6
    -se:    Seed for reproducibility
            Default: 1234
```
A sample of input csv files is included under directory ``input_data``. The format is self explanatory and can be changed.
The example ``user_group_distributions.csv`` is about 3 polarized groups of users; first group liking the first bunch of items, second the last and third the middle. This is obvious by looking at the mean column for each group.
The probability of each group is given by ``user_group_probabilities.csv``.


#### Outputs:
The following main results will be generated upon successful execution of the code:

1- ``true_user_utilities.csv``: For each user a vector of item utilities drawn from the associated group Gaussian.

2- ``simulated_data.csv``: A flat structure showing assortment at each trip for each user and the choice that user has made in that trip.

Additionally, two summaries are also generated to quickly verify the above outputs:

1- ``drawn_users_summary.csv``: Contrasts simulated group sizes and average simulated group utilities with  input group probabilities and Gaussian mean, respectively.

2- ``item_balance_per_user.csv``: Shows how balanced are assortments across user shopping trips. Per user, you would ideally want same item exposure.

## Contact:
Email me at ``a.k.ghotbi@gmail.com`` for questions and comments.

