# Bunch of Calculus terms for the card popup

DICTIONARY = [

    # Main Terms
    {
        "term": "Derivative",
        "summary": "The derivative measures the instantaneous rate of change of a function with respect to a variable.",
        "link": "https://mathworld.wolfram.com/Derivative.html",
        "tags": ["Integral","Limit", "Chain Rule", "Product Rule", "Quotient Rule", "Global Minima", "Global Maxima", "Series Expansion", "Plot", "Differential"]
    },
    {
        "term": "Integral",
        "summary": "An integral computes the area under a curve between two points. It is often called an antiderivative.",
        "link": "https://mathworld.wolfram.com/Integral.html",
        "tags": ["Derivative", "Limit", "Indefinite Integral", "Definite Integral", "Series Expansion", "Plot"]
    },
    {
        "term": "Limit",
        "summary": "A limit describes the value a function approaches as its input approaches a given point.",
        "link": "https://mathworld.wolfram.com/Limit.html",
        "tags": ["Derivative", "Integral", "Continuity", "L'Hopital's Rule"]
    },

    # Derivative children
    {
        "term": "Chain Rule",
        "summary": "The chain rule is a formula for computing the derivative of a composite function such that if y = f(g(x)), then dy/dx = f'(g(x)) · g'(x).",
        "link": "https://mathworld.wolfram.com/ChainRule.html",
        "tags": ["Derivative", "Product Rule", "Quotient Rule"]
    },
    {
        "term": "Product Rule",
        "summary": "The product rule states that the derivative of two multiplied functions f(x)g(x) is given by f'(x)g(x) + f(x)g'(x).",
        "link": "https://mathworld.wolfram.com/ProductRule.html",
        "tags": ["Derivative", "Quotient Rule", "Chain Rule"]
    },
    {
        "term": "Quotient Rule",
        "summary": "The quotient rule states that the derivative of a quotient of two functions f(x)/g(x) is given by (f'(x)g(x) - f(x)g'(x)) / (g(x))^2.",
        "link": "https://mathworld.wolfram.com/QuotientRule.html",
        "tags": ["Derivative", "Product Rule", "Chain Rule"]
    },
    {
        "term": "Global Minima",
        "summary": "A global minimum is the lowest value a function attains over its entire domain.",
        "link": "https://mathworld.wolfram.com/GlobalMinimum.html",
        "tags": ["Derivative", "Global Maxima"]
    },
    {
        "term": "Global Maxima",
        "summary": "A global maximum is the highest value a function attains over its entire domain.",
        "link": "https://mathworld.wolfram.com/GlobalMaximum.html",
        "tags": ["Derivative", "Global Minima"]
    },
    {
    "term": "Differential",
    "summary": "A differential represents an infinitely small change in a variable.",
    "link": "https://mathworld.wolfram.com/Differential.html",
    "tags": ["Derivative", "Integral", "Indefinite Integral"]
    },

    # Integral children
    {
        "term": "Indefinite Integral",
        "summary": "An indefinite integral represents the family of all antiderivatives of a function. It is the reverse operation of differentiation.",
        "link": "https://mathworld.wolfram.com/IndefiniteIntegral.html",
        "tags": ["Integral", "Definite Integral"]
    },
    {
        "term": "Definite Integral",
        "summary": "A definite integral computes the net  area under a curve between two bounds a and b. It yields a specific numeric value as opposed to a family of functions.",
        "link": "https://mathworld.wolfram.com/DefiniteIntegral.html",
        "tags": ["Integral", "Indefinite Integral"]
    },

    # Limit children
    {
        "term": "L'Hopital's Rule",
        "summary": "L'Hopital's rule resolves indeterminate forms like 0/0 or infinity/infinity by differentiating the numerator and denominator separately and retaking the limit.",
        "link": "https://mathworld.wolfram.com/LHospitalsRule.html",
        "tags": ["Limit", "Derivative"]
    },
    {
        "term": "Continuity",
        "summary": "A function is continuous at a point if its limit exists there and equals the function's value. Visually this is a function with no breaks or jumps.",
        "link": "https://mathworld.wolfram.com/Continuous.html",
        "tags": ["Limit", "Derivative"]
    },

    # Other
    {
        "term": "Series Expansion",
        "summary": "A series expansion expresses a function as an infinite sum of simpler terms These are used to approximate functions near a specific point.",
        "link": "https://mathworld.wolfram.com/SeriesExpansion.html",
        "tags": ["Derivative", "Integral", "Limit"]
    },
    {
        "term": "Plot",
        "summary": "A plot is a graphical representation of a function or equation on a cartesian plane.",
        "link": "https://mathworld.wolfram.com/FunctionGraph.html",
        "tags": ["Derivative", "Integral"]
    }

]