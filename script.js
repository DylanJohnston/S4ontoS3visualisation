const images = {
    "cycle": {
        "() = id": "() = id",    
        "(12)": "(ab)",       
        "(13)": "(ac)",       
        "(14)": "(bc)",      
        "(23)": "(bc)",        
        "(24)": "(ac)",        
        "(34)": "(ab)",        
        "(123)": "(abc)",     
        "(124)": "(acb)",       
        "(132)": "(acb)",        
        "(134)": "(abc)",       
        "(142)": "(abc)",      
        "(143)": "(acb)",      
        "(234)": "(acb)",       
        "(243)": "(abc)",      
        "(12)(34)": "() = id",   
        "(13)(24)": "() = id",  
        "(14)(23)": "() = id",  
        "(1234)": "(ac)",       
        "(1243)": "(bc)",        
        "(1324)": "(ab)",        
        "(1342)": "(bc)",     
        "(1423)": "(ab)",       
        "(1432)": "(ac)",      
    },
    "one-line": {
        "1234": "abc",    
        "2134": "bac",  
        "3214": "cba",  
        "4231": "acb",   
        "1324": "acb",   
        "1432": "cba",   
        "1243": "bac",   
        "2314": "bca",  
        "2431": "cab",  
        "3124": "cab",  
        "3241": "bca", 
        "4132": "bca",    
        "4213": "cab",  
        "1342": "cab", 
        "1423": "bca",  
        "2143": "abc",  
        "3412": "abc",   
        "4321": "abc", 
        "2341": "cba",  
        "2413": "acb", 
        "3421": "bac", 
        "3142": "acb",    
        "4312": "bac", 
        "4123": "cba",    
    }
};

const cycle_to_oneline_mapper = {
        "() = id": "1234",   
        "(12)": "2134",         
        "(13)": "3214",       
        "(14)": "4231",          
        "(23)": "1324",          
        "(24)": "1432",        
        "(34)": "1243",         
        "(123)": "2314",     
        "(124)": "2431",       
        "(132)": "3124",   
        "(134)": "3241",    
        "(142)": "4132",    
        "(143)": "4213",      
        "(234)": "1342",        
        "(243)": "1423",  
        "(12)(34)": "2143",  
        "(13)(24)": "3412", 
        "(14)(23)": "4321",  
        "(1234)": "2341", 
        "(1243)": "2413",
        "(1324)": "3421", 
        "(1342)": "3142",    
        "(1423)": "4312", 
        "(1432)": "4123", 
    }

/**
 * Takes a html select element ID and returns the textContent corresponding to option with value `value'
 * @param  {string} selectID: the id of the html select element
 * @param  {string} value: the value of the select option whose text we wish to extract
 * @return {string} textContent of the desired select element option. null if such an option cant be found.
 */
function getOptionTextByValue(selectId, value) {	
    const selectElement = document.getElementById(selectId);
    for (let i = 0; i < selectElement.options.length; i++) {
        const option = selectElement.options[i];
        if (option.value === value) {
            return option.textContent;
        }
    }    
    return null;
}

/**
 * Takes a string with parathesis and removes them e.g (12)(34) -> ['12','34']
 * @param  {string} str: the string (with parentheses).
 * @return {list} a list of strings, with each element being inners of parentheses from `str'
 */
function extractTextInsideParentheses(str) {
    // Match all text inside parentheses
    const matches = [...str.matchAll(/\(([^)]+)\)/g)];
    // Extract the text inside each match and return it as an array
    return matches.map(match => match[1]);
}

/**
 * Takes an array of strings and a character `char' and returns it's first occarence as a tuple
 * e.g. arr = ['ab','cd'], char = 'd', returns (1,1) i.e. 2nd entry of array, 2nd char of arr[1].
 * @param  {list} arr: a list of strings
 * @param  {string} char: the character (or I suppose substring) we want to find
 * @return {list} tuple with first occurance in form (index of arr, index of char). null if char can't be found.
 */
function findCharacterOccurrence(arr, char) {
    for (let i = 0; i < arr.length; i++) {
        const index = arr[i].indexOf(char);
        if (index !== -1) {
            return [i, index];
        }
    }
    return null;
}

/**
 * Takes a string, creates html to colour the letter a red, b blue and c green
 * @param  {string} str: the string we wish to colour.
 * @return {string} html with letters coloured as in function description. 
 */
function colouriseString(str) {
    const colorMap = {
        'a': 'red',
        'b': 'blue',
        'c': 'green'
    };    
    let coloredString = str.split('').map(char => {
        const color = colorMap[char];
        if (color) {
            return `<span style="color:${color};">${char}</span>`;
        }
        return char;
    }).join('');

    return coloredString;
}

document.getElementById('notation_select').addEventListener('change', function() {
    const selected_notation = this.value;
    updateS4elements(selected_notation);
    updateDescription(selected_notation);
});

document.getElementById('S4-element-select').addEventListener('change', function() {
	const selected_element = this.value
    updateDisplay(selected_element);
});

/**
 * updates the elements of S4 based on the notation chosen.
 * @param  {string} notation: the value of the option chosen in the html selector regarding the element notation type (with id='notation-select').
 */
function updateS4elements(notation) {
    const S4ElementSelect = document.getElementById('S4-element-select');
    const elements = Object.keys(images[notation]);

    S4ElementSelect.innerHTML = '';

    elements.forEach(element => {
        const option = document.createElement('option');
        option.value = element;
        option.textContent = element;
        S4ElementSelect.appendChild(option);
    });

    S4ElementSelect.selectedIndex = 0;
    const event = new Event('change');
	S4ElementSelect.dispatchEvent(event);
}

/**
 * updates everything from the displayed animation, image of element under map S4 -> S3 and explcit desciptions of the elements, based on the element chosen.
 * the function is roughly split in two, as the logic depends on whether the notation is cycle or one-line. I may merge this a bit in the future.
 * @param  {string} S4element: the value of the option chosen in the html selector reagrding choosing an element of S4 (with id='S4-element-select').
 */
function updateDisplay(S4element) {
    const selectedNotation = document.getElementById('notation_select').value;
    const GIFDiv = document.getElementById('animation');

    //update if notation is one-line
    if(selectedNotation == 'one-line'){
    	//update GIF
    	GIFDiv.src = `./GIFs/tetrahedron_reflection_swap_${S4element}.gif`;
    	//update explicit description of S4 element
    	for (let i = 1; i < 5; i++) {
    		const explicit_image = document.getElementById(`S4image${i}`);
			explicit_image.innerHTML = `${i} \\( \\mapsto \\) ${S4element[i-1]}`;  		
    		MathJax.Hub.Queue(["Typeset", MathJax.Hub, explicit_image]);
    	}
    	//update the image of S4 element (in S3).
    	img_in_S3 = document.getElementById('S3-element');
    	S3element_not_coloured = images[selectedNotation][S4element];
    	img_in_S3.innerHTML = `${colouriseString(S3element_not_coloured)}`;
    	//update explicit description of S3 element.
    	const alpha_elements = ['a','b','c']
    	alpha_elements.forEach((value,index) => {
    		const explicit_image = document.getElementById(`S3image${value}`);
    		explicit_image.innerHTML = `${colouriseString(value)} \\( \\mapsto \\) ${colouriseString(S3element_not_coloured[index])}`;
    		MathJax.Hub.Queue(["Typeset", MathJax.Hub, explicit_image]);
    	});
    }

    //update if notation is cycle
    else{
    	//update GIF
    	GIFDiv.src = `./GIFs/tetrahedron_reflection_swap_${cycle_to_oneline_mapper[S4element]}.gif`;
    	//update explicit description of S4 element
    	stripped_element = extractTextInsideParentheses(S4element)
    	for (let i = 1; i < 5; i++) {
    		const explicit_image = document.getElementById(`S4image${i}`);
    		i_index = findCharacterOccurrence(stripped_element, i.toString());
    		if(i_index == null){
    			//i.e. i does not appear in the cycle
    			explicit_image.innerHTML = `${i} \\( \\mapsto \\) ${i}`;
    		}
    		else{    			
    			explicit_image.innerHTML = `${i} \\( \\mapsto \\) ${stripped_element[i_index[0]][(i_index[1]+1) % stripped_element[i_index[0]].length]}`;
    		}
    		MathJax.Hub.Queue(["Typeset", MathJax.Hub, explicit_image]);
    	}
    	//update the image of S4 element (in S3).
    	img_in_S3 = document.getElementById('S3-element');
    	S3element = images[selectedNotation][S4element];
    	img_in_S3.innerHTML = `${colouriseString(S3element)}`;
    	//update explicit description of S3 element.
    	const alpha_elements = ['a','b','c']
    	alpha_elements.forEach((value,index) => {
    		const explicit_image = document.getElementById(`S3image${value}`);
    		const stripped_S3_element = extractTextInsideParentheses(S3element)[0];
    		let alpha_index = -1
    		try{    			
    			alpha_index = stripped_S3_element.indexOf(value);	
    		} catch (TypeError){
    			console.log("type-error associated to id in cycle notation, it's no issue, just ignore.")
    		}
    		if(alpha_index == -1){
    			//i.e. value does not appear in the cycle
    			explicit_image.innerHTML = `${colouriseString(value)} \\( \\mapsto \\) ${colouriseString(value)}`;
    		}
    		else{
    			explicit_image.innerHTML = `${colouriseString(value)} \\( \\mapsto \\) ${colouriseString(stripped_S3_element[(alpha_index+1) % stripped_S3_element.length])}`;
    		}
    		MathJax.Hub.Queue(["Typeset", MathJax.Hub, explicit_image]);
    	});
    };
};

const K4cosets = {
	1: ["() = id","(12)(34)","(13)(24)","(14)(23)"],
	2: ["(12)","(34)", "(1324)", "(1423)"],
	3: ["(13)","(1234)","(24)", "(1432)"],
	4: ["(23)", "(1342)", "(1243)", "(14)"],
	5: ["(123)", "(134)", "(243)", "(142)"],
	6: ["(132)", "(234)", "(124)", "(143)"]
};

/**
 * updates the explicit desciption of the map and kernel based on which notation was chosen.
 * @param  {string} notation: the value of the option chosen in the html selector regarding the element notation type (with id='notation-select').
 */
function updateDescription(notation){
	for(let i=1; i < 7; i++) {		
		const column = document.getElementById(`desc-column-${i}`);
		column.innerHTML = '';

		K4cosets[i].forEach(ele => {
			const line = document.createElement('p');
	        line.value = ele;
	        if(notation == 'cycle'){
	        	line.innerHTML = `${ele} \\( \\mapsto \\) ${colouriseString(images[notation][ele])}`;
	        }
	        else{
	        	//notation is one-line
	        	line.innerHTML = `${cycle_to_oneline_mapper[ele]} \\( \\mapsto \\) ${colouriseString(images[notation][cycle_to_oneline_mapper[ele]])}`;
	        }	        
	        column.appendChild(line);
	        MathJax.Hub.Queue(["Typeset", MathJax.Hub, line]);
		});
        
	}
	const K4Descriptor = document.getElementById('K4-desc')
	if(notation == 'cycle'){
    	K4Descriptor.innerHTML = `\\(K_4 = \\big\\{ \\) ${K4cosets[1].join(', ')}\\( \\big\\}. \\)`;
    	MathJax.Hub.Queue(["Typeset", MathJax.Hub, K4Descriptor]);
    }
    else{
    	//notation is one-line
    	K4Descriptor.innerHTML = `\\(K_4 = \\big\\{ \\) ${K4cosets[1].map(ele => cycle_to_oneline_mapper[ele]).join(', ')}\\( \\big\\}. \\)`;
    	MathJax.Hub.Queue(["Typeset", MathJax.Hub, K4Descriptor]);
    }
};

/**
 * set some default values when the window opens to get the ball rolling :) 
 */
window.onload = function() {
    const NotationSelector = document.getElementById('notation_select')
    NotationSelector.selectedIndex = 0;    
    const defaultNotationEvent = new Event('change');
	NotationSelector.dispatchEvent(defaultNotationEvent);
};