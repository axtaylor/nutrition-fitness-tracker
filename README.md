# Nutrition Fitness Tracker

[www.nutrition-fitness-tracker.ca/](https://www.nutrition-fitness-tracker.ca)

Nutrition Fitness Tracker is an application designed track body weight, body composition, and caloric consumption, returning caloric predictions, fitness frequency predictions, and a data dashboard featuring a live overview of many important health and nutrition markers.

### Features

- Dynamic calorie recommendations for different rates of weight loss and weight gain.
- US Navy calculations for body fat percentage, fat free (lean) mass, fat mass.
- Fat Free Mass Index (FFMI) calculator.
- Body Mass Index (BMI) calculator.
- Basal Metabolic Rate (BMR) calculator.
- Total Daily Energy Expenditure (TDEE) calculator.
- Activity level predictions.
- Bodyweight predictions at body fat percentage intervals.
- Macronutrient analysis, caloric representation of consumed macronutrients.

### Technologies

- Python 3.13, Django 5.25
- JavaScript, HTML5, CSS
- MySQL, SQLite
- Deployed on a Linux Server with PythonAnywhere


### Acknowledgements

#### Application Logic

- US Navy Body Fat Reference, [PMID: 31355083](https://pmc.ncbi.nlm.nih.gov/articles/PMC6650177)

- FFMI Reference, [PMID: 7496846](https://pubmed.ncbi.nlm.nih.gov/7496846/)

- BMI Reference, [PMID: 31082114](https://pubmed.ncbi.nlm.nih.gov/31082114/)

- BMR Reference, [PMID: 2305711](https://pubmed.ncbi.nlm.nih.gov/2305711/)


#### Development and Production

- [Django](https://www.djangoproject.com/)

- [Pythonanywhere](https://www.pythonanywhere.com/)

- [Chart.js](https://www.jsdelivr.com/package/npm/chart.js?path=dist)

### Additional Methodology

Body Fat Projections in Weight Units:

$$\text{Weight at Body Fat \%} = \frac{\text{Recorded Lean Mass}}{1-\frac{\text{ Desired Body Fat \%}}{100}}$$

Moving Total Daily Energy Expenditure (TDEE) in Calories:

$$\text{Moving TDEE} = \text{Average Calories over 28 Days} - (\frac{\text{Weight Change over 28 Days}}{4} \times 500)$$

Caloric Recommendation Amount:

$$\text{Recommendation} = \text{TDEE} \  \pm \text{Surplus or Deficit Calories} $$

Moving Daily Caloric Expenditure after BMR:

$$\text{Daily Expenditure} = \text{Moving TDEE} - \text{BMR}$$

Activity Multiplier, an approximation of exercise frequency based on the ratio of TDEE to BMR:

$$\text{Activity Multiplier} = \frac{\text{Moving TDEE}}{\text{BMR}}$$



