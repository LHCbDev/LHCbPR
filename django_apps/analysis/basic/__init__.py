'''
Choose one attribute on which you want to query on, and also choose at least one job description and press the "Retrieve results" button to get back the results(depending on the selected filters).

In case you want to generate a histogram click on the corresponding checkbok, but make sure your choices produce less than 4(max limit is 3) results else the generate histogram function won't work.

Also you can customize your histogram by typing your values on the nbins, xlow, xup input texts(only numbers are permitted) and choose whether you want the histograms(if more than one) to be separately or superimposed
'''

#this will be the title of your hmtl page

title = 'Basic analysis'

from basic import render, analyse, filterAtrs
    