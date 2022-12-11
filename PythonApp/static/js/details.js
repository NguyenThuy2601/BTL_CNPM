function setMax(obj, r1, r2) {
        if(obj.value == 1)
        {
            var child = document.getElementById('Child')
            child.setAttribute("max", r1)
            var adult = document.getElementById('Adult')
            adult.setAttribute("max", r1)
        }
        else
        {
            var child = document.getElementById('Child')
            child.setAttribute("max", r2)
            var adult = document.getElementById('Adult')
            adult.setAttribute("max", r2)
        }
 }
function changeMaxAdult(r1, r2)
    {
        adult = document.getElementById('Adult')
        child = document.getElementById('Child')
        oldValue = adult.defaultValue
        newValue = adult.value
        if(document.getElementById('class1').checked)
            ruleMax = r1
        else
            ruleMax = r2
        if(oldValue < newValue)
            newRule = ruleMax -  newValue
        else
            newRule = ruleMax + (oldValue - newValue)
        child.setAttribute("max", newRule)
        adult.defaultValue = newValue
}


function changeMaxChild(r1, r2)
{
        adult = document.getElementById('Adult')
        child = document.getElementById('Child')
        oldValue = child.defaultValue
        newValue = child.value
        if(document.getElementById('class1').checked)
            ruleMax = r1
        else
            ruleMax = r2
        if(oldValue < newValue)
            newRule = ruleMax -  newValue
        else
            newRule = ruleMax + (oldValue - newValue)
        adult.setAttribute("max", newRule)
        child.defaultValue = newValue
}