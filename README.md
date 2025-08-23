# Nutrition Fitness Tracker

[nutrition-fitness-tracker.ca](https://www.nutrition-fitness-tracker.ca)


Nutrition and Composition tracker with an emphasis on statistics and science-based tracking methodologies. 

### Features

- Dynamic caloric recommendations for varying rates of weight loss and weight gain.
- US Navy Body Fat Percentage, Fat Free (Lean) Mass, Fat Mass calculator and journal.
- Fat Free Mass Index (FFMI) calculator.
- Body Mass Index (BMI) calculator.
- Basal Metabolic Rate (BMR) calculator.
- Total Daily Energy Expenditure (TDEE) calculator.
- Activity multiplier calculator (active, sedentary..).
- Bodyweight predictions for various body fat percentage intervals.
- Macronutrient analysis, caloric representation of consumed macronutrients.
- Charts and Visualizations for Consumed Calories, Body Composition, Weight, and Nutrition.
- Preview mode and temporary user profile.


### Technologies

- Python 3.13, Django 5.25
- JavaScript, HTML5, CSS
- MySQL, SQLite
- Deployed on a Linux Server with Pythonanywhere


### Acknowledgements

#### Application Logic

- Body Fat Calculations, [PMID: 31355083](https://pmc.ncbi.nlm.nih.gov/articles/PMC6650177)

- FFMI Calculations, [PMID: 7496846](https://pubmed.ncbi.nlm.nih.gov/7496846/)

- BMI Calculations, [PMID: 31082114](https://pubmed.ncbi.nlm.nih.gov/31082114/)

- BMR Calculations, [PMID: 2305711](https://pubmed.ncbi.nlm.nih.gov/2305711/)


#### Development and Production

- [Django](https://www.djangoproject.com/), Backend framework

- [Pythonanywhere](https://www.pythonanywhere.com/), Hosting service

- [Chart.js](https://www.jsdelivr.com/package/npm/chart.js?path=dist), Data visualizations


#### Methodology

Body Fat Projections in Weight Units:

$$\text{Weight at Body Fat \%} = \frac{\text{Recorded Lean Mass}}{1-\frac{\text{ Desired Body Fat \%}}{100}}$$

Moving Total Daily Energy Expenditure (TDEE) in Calories:

$$\text{Moving TDEE} = \text{Average Calories over 28 Days} - (\frac{\text{Weight Change over 28 Days}}{4} \times 500)$$

Weight Loss and Weight Gain Recommendations in Calories:

$$\text{Recommendation} = \text{TDEE} \  \pm \text{Surplus or Deficit Calories} $$

Moving Daily Caloric Expenditure after BMR:

$$\text{Daily Expenditure} = \text{Moving TDEE} - \text{BMR}$$

Activity Multiplier, an approximation of exercise frequency based on the ratio of TDEE to BMR:

$$\text{Activity Multiplier} = \frac{\text{Moving TDEE}}{\text{BMR}}$$



