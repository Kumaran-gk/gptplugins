from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set


CHEMISTRY_TEMPLATE_BANK: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "chemical_reactions": {
        "multiple_choice": [
            {
                "stem": "Which reaction below is best classified as a synthesis reaction?",
                "options": [
                    "A. CaO + H2O -> Ca(OH)2",
                    "B. 2KClO3 -> 2KCl + 3O2",
                    "C. Zn + CuSO4 -> ZnSO4 + Cu",
                    "D. HCl + NaOH -> NaCl + H2O",
                ],
                "answer_hint": "A",
            },
            {
                "stem": "Which reaction below is best classified as a single displacement reaction?",
                "options": [
                    "A. Fe + CuSO4 -> FeSO4 + Cu",
                    "B. 2H2O -> 2H2 + O2",
                    "C. CH4 + 2O2 -> CO2 + 2H2O",
                    "D. AgNO3 + NaCl -> AgCl + NaNO3",
                ],
                "answer_hint": "A",
            },
            {
                "stem": "Which products are most likely formed when magnesium reacts with hydrochloric acid?",
                "options": [
                    "A. MgCl + H",
                    "B. MgCl2 + H2",
                    "C. MgH2 + Cl2",
                    "D. Mg2Cl + H2",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Which products are formed when calcium carbonate reacts with hydrochloric acid?",
                "options": [
                    "A. CaCl2 + H2",
                    "B. CaCl2 + H2O + CO2",
                    "C. Ca + Cl2 + H2O",
                    "D. CaO + HCl",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Which pair of reactants is most likely to undergo a double displacement reaction?",
                "options": [
                    "A. Na + Cl2",
                    "B. CH4 + O2",
                    "C. AgNO3 + NaCl",
                    "D. Mg + O2",
                ],
                "answer_hint": "C",
            },
            {
                "stem": "Which balanced equation represents the complete combustion of propane?",
                "options": [
                    "A. C3H8 + 3O2 -> 3CO + 4H2O",
                    "B. C3H8 + 4O2 -> 3CO2 + 4H2O",
                    "C. C3H8 + 5O2 -> 3CO2 + 4H2O",
                    "D. 2C3H8 + 7O2 -> 6CO2 + 8H2O",
                ],
                "answer_hint": "C",
            },
            {
                "stem": "Which equation represents a decomposition reaction?",
                "options": [
                    "A. 2HgO -> 2Hg + O2",
                    "B. 2Mg + O2 -> 2MgO",
                    "C. HCl + NaOH -> NaCl + H2O",
                    "D. Fe + CuSO4 -> FeSO4 + Cu",
                ],
                "answer_hint": "A",
            },
            {
                "stem": "Which pair of aqueous solutions is most likely to produce a precipitate?",
                "options": [
                    "A. NaNO3 + KCl",
                    "B. BaCl2 + Na2SO4",
                    "C. HCl + H2O",
                    "D. KOH + NaOH",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Which equation is correctly balanced for the formation of magnesium oxide?",
                "options": [
                    "A. Mg + O2 -> MgO2",
                    "B. 2Mg + O2 -> 2MgO",
                    "C. Mg + O -> MgO",
                    "D. Mg2 + O2 -> 2MgO",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Which reaction is an example of decomposition?",
                "options": [
                    "A. 2H2O2 -> 2H2O + O2",
                    "B. Mg + 2HCl -> MgCl2 + H2",
                    "C. NaOH + HCl -> NaCl + H2O",
                    "D. 2Na + Cl2 -> 2NaCl",
                ],
                "answer_hint": "A",
            },
            {
                "stem": "Which products are most likely formed when zinc reacts with copper(II) sulfate?",
                "options": [
                    "A. ZnCu + SO4",
                    "B. ZnSO4 + Cu",
                    "C. CuSO4 + Zn2",
                    "D. ZnO + CuS",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Which statement best describes incomplete combustion?",
                "options": [
                    "A. It always produces only carbon dioxide and water",
                    "B. It occurs when oxygen is abundant",
                    "C. It can produce carbon monoxide and soot",
                    "D. It is the same as neutralization",
                ],
                "answer_hint": "C",
            },
            {
                "stem": "Which products are expected from the neutralization of sulfuric acid and sodium hydroxide?",
                "options": [
                    "A. Na2SO4 + H2O",
                    "B. NaSO4 + H2",
                    "C. SO2 + NaOH",
                    "D. Na2S + O2 + H2O",
                ],
                "answer_hint": "A",
            },
            {
                "stem": "Which observation most strongly supports that a gas-forming reaction has occurred?",
                "options": [
                    "A. The solution stays perfectly still",
                    "B. Bubbling or effervescence appears",
                    "C. The beaker mass increases sharply without a lid",
                    "D. The reactants become elements only",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Which reactant pair is most likely to undergo an acid-carbonate reaction?",
                "options": [
                    "A. HCl + CaCO3",
                    "B. NaCl + KNO3",
                    "C. O2 + Ne",
                    "D. Ag + Au",
                ],
                "answer_hint": "A",
            },
            {
                "stem": "Which products are formed when sodium oxide reacts with sulfur trioxide?",
                "options": [
                    "A. Na2SO4",
                    "B. NaSO3 + O2",
                    "C. Na + SO4",
                    "D. Na2S + O3",
                ],
                "answer_hint": "A",
            },
        ],
        "written_response": [
            {
                "stem": "Predict the products, balance the equation, and classify the reaction:\nAl + O2 ->",
                "answer_hint": "Al2O3; balanced form 4Al + 3O2 -> 2Al2O3; synthesis",
            },
            {
                "stem": "Complete, balance, and classify the reaction:\nCaCO3 ->",
                "answer_hint": "CaO + CO2; decomposition",
            },
            {
                "stem": "Write the balanced equation with states for the reaction between silver nitrate and sodium chloride.",
                "answer_hint": "AgNO3(aq) + NaCl(aq) -> AgCl(s) + NaNO3(aq)",
            },
            {
                "stem": "Predict the products and balance the following reaction:\nZn + CuSO4 ->",
                "answer_hint": "ZnSO4 + Cu; single displacement",
            },
            {
                "stem": "Predict the products, include states, balance the equation, and classify the reaction:\nAgNO3(aq) + MgBr2(aq) ->",
                "answer_hint": "2AgNO3(aq) + MgBr2(aq) -> 2AgBr(s) + Mg(NO3)2(aq); double displacement / precipitation",
            },
            {
                "stem": "Complete, balance, and classify the reaction:\nMg + Br2 ->",
                "answer_hint": "MgBr2; synthesis",
            },
            {
                "stem": "Complete, balance, and classify the reaction:\nNa2O + SO3 ->",
                "answer_hint": "Na2SO4; synthesis",
            },
            {
                "stem": "Write the balanced equation with states for the neutralization of phosphoric acid by potassium hydroxide.",
                "answer_hint": "3KOH(aq) + H3PO4(aq) -> K3PO4(aq) + 3H2O(l)",
            },
            {
                "stem": "Write a balanced equation for the complete combustion of methane and classify the reaction.",
                "answer_hint": "CH4 + 2O2 -> CO2 + 2H2O; combustion",
            },
            {
                "stem": "Predict the products, balance the equation, and classify the reaction:\nCu + Cl2 ->",
                "answer_hint": "CuCl2; synthesis",
            },
        ],
        "application": [
            {
                "stem": "Methane burns in oxygen. Explain how the products differ in complete combustion versus incomplete combustion, and write one balanced equation for complete combustion.",
                "answer_hint": "Complete combustion produces CO2 and H2O; incomplete may produce CO and/or C; CH4 + 2O2 -> CO2 + 2H2O",
            },
            {
                "stem": "A student mixes two clear ionic solutions and a precipitate forms. Explain what this suggests about the reaction type and give one possible balanced example.",
                "answer_hint": "Likely double displacement / precipitation reaction; example AgNO3 + NaCl -> AgCl + NaNO3",
            },
            {
                "stem": "An engine is not getting enough oxygen during fuel combustion. Predict one likely chemical consequence and explain why it matters in a real-world context.",
                "answer_hint": "Incomplete combustion may produce CO and/or soot; real-world concern includes toxicity and pollution.",
            },
            {
                "stem": "Argentite ore contains silver sulfide, Ag2S. Explain how a displacement reaction could be used to help isolate silver, and include a balanced chemical equation in your response.",
                "answer_hint": "Accept a valid displacement-based explanation tied to silver extraction; balanced equation should be chemically consistent with the chosen method.",
            },
            {
                "stem": "An antacid tablet containing calcium carbonate reacts with stomach acid. Explain why this is a neutralization-related process and include a balanced equation with states.",
                "answer_hint": "CaCO3(s) + 2HCl(aq) -> CaCl2(aq) + H2O(l) + CO2(g); explanation should connect acid reduction to reaction products.",
            },
            {
                "stem": "A propane barbecue is moved into a garage during rain. Explain why this is unsafe using ideas from combustion and gas production.",
                "answer_hint": "Limited oxygen can lead to incomplete combustion and carbon monoxide production; enclosed spaces increase poisoning and fire risk.",
            },
            {
                "stem": "A clear acid spill is neutralized and no visible change is observed. Describe how you could prove the reaction occurred and the area is safe to clean.",
                "answer_hint": "Use an indicator or pH probe to show the spill is near neutral; accept mention of temperature change or product evidence if justified.",
            },
        ],
    },
    "stoichiometry": {
        "multiple_choice": [
            {
                "stem": "What is the molar mass of water, H2O?",
                "options": [
                    "A. 16.00 g/mol",
                    "B. 18.02 g/mol",
                    "C. 20.00 g/mol",
                    "D. 34.02 g/mol",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "How many moles are in 22.0 g of carbon dioxide, CO2?",
                "options": [
                    "A. 0.25 mol",
                    "B. 0.50 mol",
                    "C. 1.00 mol",
                    "D. 2.00 mol",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "Calculate the number of moles in 36.0 g of water.",
                "answer_hint": "2.00 mol H2O",
            },
            {
                "stem": "Determine the molar mass of calcium carbonate, CaCO3.",
                "answer_hint": "100.09 g/mol approximately",
            },
            {
                "stem": "Calculate the number of moles in 44.0 g of carbon dioxide.",
                "answer_hint": "1.00 mol CO2",
            },
            {
                "stem": "Calculate the amount of substance in moles for 4.52 × 10^23 formula units of magnesium chloride, MgCl2(s).",
                "answer_hint": "0.751 mol MgCl2 approximately",
            },
            {
                "stem": "Calculate the mass of 0.825 mol of sodium carbonate, Na2CO3(s).",
                "answer_hint": "87.4 g Na2CO3 approximately",
            },
            {
                "stem": "How many atoms of oxygen are present in 1.50 mol of carbon dioxide, CO2(g)?",
                "answer_hint": "1.81 × 10^24 oxygen atoms approximately",
            },
            {
                "stem": "A compound is 40.0% carbon, 6.7% hydrogen, and 53.3% oxygen by mass. Its molar mass is 60.0 g/mol. Determine the molecular formula.",
                "answer_hint": "CH2O is the empirical formula; molecular formula C2H4O2",
            },
            {
                "stem": "In excess oxygen, magnesium burns to form magnesium oxide. Calculate the amount in moles of MgO produced from 12.0 g of magnesium.",
                "answer_hint": "0.494 mol MgO approximately after using the 2Mg + O2 -> 2MgO ratio",
            },
            {
                "stem": "Hydrochloric acid reacts with sodium hydroxide to form sodium chloride and water. If 0.250 mol of HCl reacts completely, what mass of NaCl is produced? Write the balanced equation.",
                "answer_hint": "HCl + NaOH -> NaCl + H2O; 14.6 g NaCl approximately",
            },
            {
                "stem": "Aqueous sulfuric acid reacts with aqueous potassium hydroxide. If 3.25 g of H2SO4 reacts with excess KOH, calculate the mass of potassium sulfate produced. Write the balanced equation.",
                "answer_hint": "H2SO4 + 2KOH -> K2SO4 + 2H2O; 5.74 g K2SO4 approximately",
            },
        ],
        "application": [
            {
                "stem": "A reaction requires 0.50 mol of oxygen gas. Calculate the mass of oxygen needed.",
                "answer_hint": "16.0 g O2",
            },
            {
                "stem": "A sample contains 1.50 mol of sodium chloride. Determine the mass of the sample.",
                "answer_hint": "Approximately 87.7 g NaCl",
            },
            {
                "stem": "A sample of silver nitrate reacts with excess calcium chloride to form silver chloride precipitate. Theoretical yield is 1.36 g AgCl, but only 1.09 g is collected dry. Calculate the percentage yield and state what this result means.",
                "answer_hint": "80.1% yield approximately; actual yield is lower than theoretical, likely due to product loss or incomplete recovery.",
            },
            {
                "stem": "A student records the following data for a precipitation reaction: 1.52 g of Pb(NO3)2 is used, excess KI is added, filter paper mass is 1.10 g, and dried precipitate plus paper is 2.26 g. Determine the experimental mass of precipitate and then calculate the percentage yield if the theoretical yield is 1.24 g.",
                "answer_hint": "Experimental precipitate mass = 1.16 g; percentage yield = 93.5% approximately.",
            },
            {
                "stem": "Aqueous hydrogen sulfide reacts with aqueous sodium hydroxide to produce sodium sulfide and water. If 2.40 g of H2S reacts with excess NaOH, calculate the mass of Na2S produced and include the balanced equation.",
                "answer_hint": "H2S + 2NaOH -> Na2S + 2H2O; 3.19 g Na2S approximately",
            },
            {
                "stem": "Lab data show that 1.48 g of AgNO3 is used, filter paper has a mass of 1.27 g, and dry precipitate plus paper has a mass of 2.36 g. Excess CaCl2(aq) is added. Determine the percentage yield of AgCl(s). Use the balanced equation 2AgNO3(aq) + CaCl2(aq) -> 2AgCl(s) + Ca(NO3)2(aq).",
                "answer_hint": "Experimental precipitate mass = 1.09 g; theoretical yield from 1.48 g AgNO3 is about 1.32 g AgCl; percentage yield is about 82.4%.",
            },
        ],
    },
    "lab_and_applications": {
        "multiple_choice": [
            {
                "stem": "Why is it important to include state symbols in a chemical equation when required?",
                "options": [
                    "A. They are decorative only",
                    "B. They show the physical state of each substance",
                    "C. They replace coefficients",
                    "D. They determine atomic mass",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Which statement best explains why clear notation matters in chemistry?",
                "options": [
                    "A. It reduces the need for observations",
                    "B. It helps communicate substances and reactions accurately",
                    "C. It removes all experimental uncertainty",
                    "D. It changes the outcome of the reaction",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "What does a blue Bunsen burner flame usually indicate compared with an orange flame?",
                "options": [
                    "A. Less oxygen and cooler burning",
                    "B. More oxygen and more complete combustion",
                    "C. No combustion is occurring",
                    "D. Water is the only product",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Which test result would best show that a neutralized spill is now safe to clean up?",
                "options": [
                    "A. The pH is close to 7",
                    "B. The liquid is darker in color",
                    "C. The container feels heavier",
                    "D. The reactants are still separate",
                ],
                "answer_hint": "A",
            },
            {
                "stem": "Why can missing state symbols still cost marks even if the products are correct?",
                "options": [
                    "A. State symbols replace balancing",
                    "B. They are required chemical notation and communicate important information",
                    "C. They change the identity of all elements",
                    "D. They are only needed in physics",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Which statement best compares orange and blue burner flames?",
                "options": [
                    "A. The orange flame is usually hotter and cleaner",
                    "B. The blue flame gives less heat but more soot",
                    "C. The blue flame is usually hotter and gives more complete combustion",
                    "D. They always produce exactly the same products",
                ],
                "answer_hint": "C",
            },
            {
                "stem": "Which observation best suggests that a precipitate has formed?",
                "options": [
                    "A. A solid appears in a previously clear mixture",
                    "B. The solution becomes a gas only",
                    "C. The pH always becomes exactly 7",
                    "D. The mass of each atom changes",
                ],
                "answer_hint": "A",
            },
            {
                "stem": "Which result would best support the claim that combustion became more complete after adjusting a burner?",
                "options": [
                    "A. The flame becomes bluer and less luminous",
                    "B. The flame becomes cooler and more orange",
                    "C. The reactants stop reacting",
                    "D. The beaker disappears",
                ],
                "answer_hint": "A",
            },
            {
                "stem": "Why might a teacher require full sentences on application questions in chemistry?",
                "options": [
                    "A. To reduce the need for chemistry vocabulary",
                    "B. To show reasoning and communicate chemical ideas clearly",
                    "C. To avoid using equations entirely",
                    "D. To make balancing unnecessary",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Which piece of evidence would best show that an acid spill has been successfully neutralized?",
                "options": [
                    "A. The solution remains colorless only",
                    "B. The pH is near neutral after treatment",
                    "C. The container is larger than before",
                    "D. The reactants are still listed separately",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "Why is using correct chemical notation important when recording observations and equations in a chemistry lab?",
                "answer_hint": "It improves clarity, communicates states and substances accurately, and reduces interpretation errors.",
            },
            {
                "stem": "Describe one real-world application of combustion reactions and one safety concern associated with it.",
                "answer_hint": "Vehicle engines / heating systems; safety concerns include toxic gases, fire risk, incomplete combustion.",
            },
            {
                "stem": "Explain why a blue Bunsen burner flame is preferred for heating in the lab.",
                "answer_hint": "It indicates more complete combustion, gives a hotter flame, and reduces soot formation.",
            },
            {
                "stem": "Describe what evidence you would record to show a chemical reaction occurred even when the solution stays clear.",
                "answer_hint": "Accept pH change, gas formation, temperature change, conductivity change, or formation of dissolved products where justified.",
            },
        ],
        "application": [
            {
                "stem": "Silver is used in batteries, jewelry, and water purification systems. Explain how chemical properties influence one of these uses.",
                "answer_hint": "Accept reasonable chemistry-based explanation tied to conductivity, reactivity, or ion behavior.",
            },
            {
                "stem": "A student reports the correct products of a reaction but forgets to include state symbols. Explain why that can still cost marks in a chemistry assessment.",
                "answer_hint": "Because notation precision is part of chemical communication and may be explicitly required.",
            },
            {
                "stem": "A student lights a Bunsen burner and leaves it with a luminous orange flame. Explain what adjustment should be made and why.",
                "answer_hint": "Open the air intake to admit more oxygen so combustion is more complete and the flame becomes hotter and cleaner.",
            },
            {
                "stem": "A teacher asks for the tests and expected results after a neutralization cleanup. Explain what a strong response should include.",
                "answer_hint": "A strong response names a suitable test such as pH paper or a pH probe and states the expected near-neutral result, with chemistry reasoning.",
            },
        ],
    },
}

PHYSICS_TEMPLATE_BANK: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "forces_and_motion": {
        "multiple_choice": [
            {
                "stem": "Which quantity is a vector?",
                "options": [
                    "A. Speed",
                    "B. Distance",
                    "C. Velocity",
                    "D. Mass",
                ],
                "answer_hint": "C",
            },
            {
                "stem": "If the net force on an object is zero, what can be true?",
                "options": [
                    "A. The object must be accelerating",
                    "B. The object may be at rest or moving at constant velocity",
                    "C. The object must be moving in a circle",
                    "D. The object must have no mass",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "Draw and describe the forces acting on a book resting on a table.",
                "answer_hint": "Weight downward and normal force upward, equal in magnitude.",
            },
            {
                "stem": "State Newton’s second law and explain the relationship among net force, mass, and acceleration.",
                "answer_hint": "F_net = ma; acceleration increases with force and decreases with mass.",
            },
        ],
        "application": [
            {
                "stem": "Explain why passengers lurch forward when a car suddenly stops.",
                "answer_hint": "Inertia causes passengers to continue moving forward until another force acts.",
            },
        ],
    },
    "energy": {
        "multiple_choice": [
            {
                "stem": "Which quantity depends on both mass and speed?",
                "options": [
                    "A. Gravitational field strength",
                    "B. Kinetic energy",
                    "C. Temperature",
                    "D. Voltage",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "What happens to gravitational potential energy as height increases?",
                "options": [
                    "A. It decreases",
                    "B. It stays the same",
                    "C. It increases",
                    "D. It becomes zero",
                ],
                "answer_hint": "C",
            },
        ],
        "written_response": [
            {
                "stem": "Write the equation for kinetic energy and define each variable.",
                "answer_hint": "KE = 1/2 mv^2; m is mass and v is speed.",
            },
            {
                "stem": "Explain the law of conservation of energy in a simple mechanical system.",
                "answer_hint": "Energy changes form but total energy remains constant if losses are negligible.",
            },
        ],
        "application": [
            {
                "stem": "A cyclist moves down a hill. Explain how energy changes during the motion.",
                "answer_hint": "Gravitational potential energy decreases while kinetic energy increases; some energy may be lost to heat/friction.",
            },
        ],
    },
    "electricity": {
        "multiple_choice": [
            {
                "stem": "Which unit is used for electric current?",
                "options": [
                    "A. Volt",
                    "B. Ohm",
                    "C. Ampere",
                    "D. Watt",
                ],
                "answer_hint": "C",
            },
            {
                "stem": "What happens to the total resistance when resistors are added in series?",
                "options": [
                    "A. It decreases",
                    "B. It stays the same",
                    "C. It increases",
                    "D. It becomes zero",
                ],
                "answer_hint": "C",
            },
        ],
        "written_response": [
            {
                "stem": "State Ohm’s law and explain the meaning of each variable.",
                "answer_hint": "V = IR; voltage equals current times resistance.",
            },
            {
                "stem": "Explain the difference between current and potential difference.",
                "answer_hint": "Current is the rate of flow of charge; potential difference is energy transferred per unit charge.",
            },
        ],
        "application": [
            {
                "stem": "Why might household circuits be wired in parallel rather than in series?",
                "answer_hint": "Parallel branches allow devices to operate independently and receive full supply voltage.",
            },
        ],
    },
    "waves_and_light": {
        "multiple_choice": [
            {
                "stem": "Which wave property is measured in hertz?",
                "options": [
                    "A. Amplitude",
                    "B. Frequency",
                    "C. Speed",
                    "D. Wavelength squared",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "What usually happens when light passes from air into glass?",
                "options": [
                    "A. It disappears",
                    "B. It always speeds up",
                    "C. It refracts",
                    "D. It becomes sound",
                ],
                "answer_hint": "C",
            },
        ],
        "written_response": [
            {
                "stem": "Define wavelength and frequency.",
                "answer_hint": "Wavelength is the distance between identical points on successive waves; frequency is the number of cycles per second.",
            },
        ],
        "application": [
            {
                "stem": "Explain why a straw appears bent when placed in a glass of water.",
                "answer_hint": "Light refracts when passing between water and air, changing apparent position.",
            },
        ],
    },
}

MATH_TEMPLATE_BANK: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "algebra": {
        "multiple_choice": [
            {
                "stem": "Which expression is equivalent to (x + 3)(x - 2)?",
                "options": [
                    "A. x^2 + x - 6",
                    "B. x^2 - x - 6",
                    "C. x^2 + 5x - 6",
                    "D. x^2 - 5x - 6",
                ],
                "answer_hint": "A",
            },
            {
                "stem": "Which value of x satisfies 2x + 5 = 17?",
                "options": [
                    "A. 5",
                    "B. 6",
                    "C. 7",
                    "D. 8",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "Solve: 3x - 7 = 14",
                "answer_hint": "x = 7",
            },
            {
                "stem": "Expand and simplify: (x + 4)(x - 1)",
                "answer_hint": "x^2 + 3x - 4",
            },
        ],
        "application": [
            {
                "stem": "A rectangle has side lengths x + 2 and x - 1. Write an expression for its area and simplify.",
                "answer_hint": "(x + 2)(x - 1) = x^2 + x - 2",
            },
        ],
    },
    "functions": {
        "multiple_choice": [
            {
                "stem": "What is the y-intercept of y = 2x + 5?",
                "options": [
                    "A. 2",
                    "B. 5",
                    "C. -5",
                    "D. 7",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Which point lies on the graph of y = x^2?",
                "options": [
                    "A. (2, 2)",
                    "B. (2, 4)",
                    "C. (4, 2)",
                    "D. (1, 0)",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "State the domain and range of the function y = x^2.",
                "answer_hint": "Domain: all real numbers; Range: y ≥ 0",
            },
            {
                "stem": "Describe the effect of translating y = x^2 to y = (x - 3)^2 + 1.",
                "answer_hint": "Right 3 units and up 1 unit.",
            },
        ],
        "application": [
            {
                "stem": "A ball’s height is modeled by a quadratic function. Explain what the vertex represents in context.",
                "answer_hint": "The vertex represents the maximum height (or minimum, depending on context) and when it occurs.",
            },
        ],
    },
    "trigonometry": {
        "multiple_choice": [
            {
                "stem": "What is sin(30°)?",
                "options": [
                    "A. 1/2",
                    "B. √3/2",
                    "C. 1",
                    "D. 0",
                ],
                "answer_hint": "A",
            },
            {
                "stem": "Which ratio is defined as opposite over hypotenuse?",
                "options": [
                    "A. cos",
                    "B. tan",
                    "C. sin",
                    "D. sec",
                ],
                "answer_hint": "C",
            },
            {
                "stem": "Which law is most useful when two sides and the included angle are known in an oblique triangle?",
                "options": [
                    "A. Sine law",
                    "B. Cosine law",
                    "C. Pythagorean theorem only",
                    "D. Tangent ratio only",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "Find the exact value of cos(60°).",
                "answer_hint": "1/2",
            },
            {
                "stem": "State one trigonometric identity involving tan x.",
                "answer_hint": "tan x = sin x / cos x",
            },
            {
                "stem": "Use the sine law to solve for the missing side in a suitable triangle problem.",
                "answer_hint": "Accept correct setup and solution using the sine law.",
            },
        ],
        "application": [
            {
                "stem": "A ladder leans against a wall. Explain how trigonometry can be used to find the height reached by the ladder.",
                "answer_hint": "Use a trig ratio such as sin or cos depending on known side and angle information.",
            },
        ],
    },
    "exponentials_and_finance": {
        "multiple_choice": [
            {
                "stem": "Which expression represents compound growth?",
                "options": [
                    "A. A = P + rt",
                    "B. A = P(1 + i)^n",
                    "C. A = P - i/n",
                    "D. A = Pi/n",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "What does a negative exponent indicate?",
                "options": [
                    "A. A larger base",
                    "B. Reciprocal relationship",
                    "C. No solution",
                    "D. Addition",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "Evaluate 2^-3.",
                "answer_hint": "1/8",
            },
            {
                "stem": "State the difference between simple interest and compound interest.",
                "answer_hint": "Simple interest is calculated on the original principal only; compound interest is calculated on accumulated amount.",
            },
        ],
        "application": [
            {
                "stem": "An investment earns 5% compound interest annually. Explain the meaning of the exponent in the compound interest formula.",
                "answer_hint": "The exponent represents the number of compounding periods.",
            },
        ],
    },
    "sequences": {
        "multiple_choice": [
            {
                "stem": "What is the common difference in the sequence 3, 7, 11, 15, ... ?",
                "options": [
                    "A. 2",
                    "B. 3",
                    "C. 4",
                    "D. 5",
                ],
                "answer_hint": "C",
            },
            {
                "stem": "Which type of sequence has a constant ratio?",
                "options": [
                    "A. Arithmetic",
                    "B. Geometric",
                    "C. Linear only",
                    "D. Recursive only",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "Write the next three terms of the arithmetic sequence 5, 9, 13, ...",
                "answer_hint": "17, 21, 25",
            },
            {
                "stem": "State the recursive rule for the geometric sequence 2, 6, 18, ...",
                "answer_hint": "Multiply each term by 3; a_n = 3a_(n-1), with first term 2",
            },
        ],
        "application": [
            {
                "stem": "Explain one real-world situation that can be modeled by a geometric sequence.",
                "answer_hint": "Examples include repeated percent growth/decay, population change, or compound interest.",
            },
        ],
    },
}

BIOLOGY_TEMPLATE_BANK: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "cells_and_systems": {
        "multiple_choice": [
            {
                "stem": "Which organelle is primarily responsible for energy production in eukaryotic cells?",
                "options": [
                    "A. Nucleus",
                    "B. Ribosome",
                    "C. Mitochondrion",
                    "D. Golgi apparatus",
                ],
                "answer_hint": "C",
            },
            {
                "stem": "Which process describes movement of water across a selectively permeable membrane?",
                "options": [
                    "A. Diffusion",
                    "B. Osmosis",
                    "C. Respiration",
                    "D. Digestion",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "State one function of the cell membrane.",
                "answer_hint": "Controls movement of substances into and out of the cell.",
            },
            {
                "stem": "Explain the difference between diffusion and osmosis.",
                "answer_hint": "Diffusion is movement of particles from high to low concentration; osmosis is the movement of water across a selectively permeable membrane.",
            },
        ],
        "application": [
            {
                "stem": "Explain why plant cells behave differently from animal cells in a hypotonic environment.",
                "answer_hint": "Plant cells become turgid because of the cell wall; animal cells may swell more significantly without a rigid wall.",
            },
        ],
    },
    "genetics": {
        "multiple_choice": [
            {
                "stem": "Which molecule carries hereditary information?",
                "options": [
                    "A. ATP",
                    "B. DNA",
                    "C. Glucose",
                    "D. Lipid",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Different forms of the same gene are called:",
                "options": [
                    "A. Cells",
                    "B. Alleles",
                    "C. Tissues",
                    "D. Enzymes",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "Define the term allele.",
                "answer_hint": "An allele is an alternative form of a gene.",
            },
            {
                "stem": "Explain the difference between genotype and phenotype.",
                "answer_hint": "Genotype is the genetic makeup; phenotype is the observable trait.",
            },
        ],
        "application": [
            {
                "stem": "Explain how a Punnett square can help predict offspring traits.",
                "answer_hint": "It organizes allele combinations and shows possible genotypes/phenotypes for offspring.",
            },
        ],
    },
    "evolution": {
        "multiple_choice": [
            {
                "stem": "Which concept is most closely associated with natural selection?",
                "options": [
                    "A. Identical offspring in all environments",
                    "B. Survival and reproduction of better-adapted organisms",
                    "C. No variation within populations",
                    "D. Instant species change",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Variation within a population is important because it:",
                "options": [
                    "A. Prevents all inheritance",
                    "B. Provides material on which natural selection can act",
                    "C. Removes environmental effects",
                    "D. Stops mutation",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "Define natural selection.",
                "answer_hint": "Natural selection is the process by which individuals with advantageous traits survive and reproduce more successfully.",
            },
        ],
        "application": [
            {
                "stem": "Explain how antibiotic resistance in bacteria provides evidence for evolution.",
                "answer_hint": "Resistant bacteria survive and reproduce, increasing the frequency of resistance traits in the population.",
            },
        ],
    },
    "ecology": {
        "multiple_choice": [
            {
                "stem": "Which term refers to all the organisms of one species living in the same area?",
                "options": [
                    "A. Community",
                    "B. Ecosystem",
                    "C. Population",
                    "D. Habitat",
                ],
                "answer_hint": "C",
            },
            {
                "stem": "Which level includes both living and non-living components?",
                "options": [
                    "A. Population",
                    "B. Ecosystem",
                    "C. Species only",
                    "D. Niche only",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "State the difference between a population and a community.",
                "answer_hint": "A population is one species in an area; a community is multiple interacting populations in an area.",
            },
            {
                "stem": "Explain why biodiversity is important in an ecosystem.",
                "answer_hint": "Greater biodiversity can improve stability, resilience, and ecological balance.",
            },
        ],
        "application": [
            {
                "stem": "Describe one possible ecological consequence of removing a top predator from an ecosystem.",
                "answer_hint": "May disrupt food webs, cause prey populations to increase, and change ecosystem balance.",
            },
        ],
    },
}

GENERIC_TEMPLATE_BANK: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    "general_content": {
        "multiple_choice": [
            {
                "stem": "Which statement is most accurate about the topic being assessed in this section?",
                "options": [
                    "A. It depends on a single isolated fact only",
                    "B. It combines concept knowledge with careful interpretation",
                    "C. It cannot be evaluated using evidence",
                    "D. It has no relationship to the unit goals",
                ],
                "answer_hint": "B",
            },
            {
                "stem": "Which choice best reflects the kind of reasoning required in this section?",
                "options": [
                    "A. Guesswork only",
                    "B. Careful use of evidence and method",
                    "C. Memorization without understanding",
                    "D. Random selection",
                ],
                "answer_hint": "B",
            },
        ],
        "written_response": [
            {
                "stem": "Answer a fresh question that demonstrates understanding of the main concept in this section.",
                "answer_hint": "Use the blueprint topic and section style to replace this with a richer subject-specific item later.",
            },
            {
                "stem": "Explain the central idea from this section using an appropriate example.",
                "answer_hint": "Use a subject-aligned explanation with a clear supporting example.",
            },
        ],
        "application": [
            {
                "stem": "Apply the main concept from this section to a new example or real-world scenario.",
                "answer_hint": "Use a context aligned to the blueprint topic and difficulty.",
            },
            {
                "stem": "Use the concept from this section to explain a practical or real-world situation.",
                "answer_hint": "Accept a valid applied explanation tied to the section topic.",
            },
        ],
    }
}

SUBJECT_TEMPLATE_BANKS: Dict[str, Dict[str, Dict[str, List[Dict[str, Any]]]]] = {
    "chemistry": CHEMISTRY_TEMPLATE_BANK,
    "physics": PHYSICS_TEMPLATE_BANK,
    "math": MATH_TEMPLATE_BANK,
    "biology": BIOLOGY_TEMPLATE_BANK,
}

CHALLENGING_TEMPLATE_BANKS: Dict[str, Dict[str, Dict[str, List[Dict[str, Any]]]]] = {
    "chemistry": {
        "chemical_reactions": {
            "multiple_choice": [
                {
                    "stem": "A student predicts products for a reaction between aluminum sulfate and calcium hydroxide. Which outcome is most chemically reasonable after balancing and considering solubility?",
                    "options": [
                        "A. Al(OH)3(s) + CaSO4(aq)",
                        "B. 2Al(OH)3(s) + 3CaSO4(aq)",
                        "C. Al2O3(s) + CaSO4(aq) + H2O(l)",
                        "D. Al(s) + CaSO4(aq) + OH-(aq)",
                    ],
                    "answer_hint": "B",
                },
                {
                    "stem": "Which balanced equation best represents a single displacement reaction that is actually likely to occur based on the activity of the metals involved?",
                    "options": [
                        "A. Cu + MgSO4 -> CuSO4 + Mg",
                        "B. Zn + CuSO4 -> ZnSO4 + Cu",
                        "C. Ag + NaCl -> AgCl + Na",
                        "D. Au + HCl -> AuCl3 + H2",
                    ],
                    "answer_hint": "B",
                },
                {
                    "stem": "Which option best explains why the same hydrocarbon can produce different carbon-containing products under complete versus incomplete combustion?",
                    "options": [
                        "A. Carbon changes atomic number during the reaction",
                        "B. Oxygen availability changes how fully carbon is oxidized",
                        "C. Hydrogen stops reacting when temperature rises",
                        "D. State symbols determine the final products",
                    ],
                    "answer_hint": "B",
                },
            ],
            "written_response": [
                {
                    "stem": "Predict the products, include states, balance the equation, classify the reaction, and briefly justify why a precipitate is expected:\nAl2(SO4)3(aq) + Ca(OH)2(aq) ->",
                    "answer_hint": "Al2(SO4)3(aq) + 3Ca(OH)2(aq) -> 2Al(OH)3(s) + 3CaSO4(aq); double displacement / precipitation; justification should reference insoluble aluminum hydroxide.",
                },
                {
                    "stem": "A metal carbonate is heated strongly and forms a metal oxide plus a gas. Write a balanced example equation, classify the reaction, and explain the evidence that would support your classification.",
                    "answer_hint": "Accept a valid decomposition example such as CaCO3 -> CaO + CO2; response should identify decomposition and mention gas release and formation of two products from one reactant.",
                },
                {
                    "stem": "Write a balanced equation with states for a neutralization that also produces a gas, and explain why it is not classified as a simple synthesis reaction.",
                    "answer_hint": "Accept an acid-carbonate example such as CaCO3(s) + 2HCl(aq) -> CaCl2(aq) + H2O(l) + CO2(g); explanation should distinguish neutralization / gas evolution from synthesis.",
                },
            ],
            "application": [
                {
                    "stem": "A student proposes that every reaction producing a solid must be synthesis. Evaluate this claim using one counterexample equation and explain the correct classification.",
                    "answer_hint": "A strong response rejects the claim, gives a precipitation / double displacement example such as AgNO3 + NaCl -> AgCl + NaNO3, and explains why solid formation alone does not determine synthesis.",
                },
                {
                    "stem": "During a lab, two groups obtain different products for the combustion of the same hydrocarbon sample. Explain how oxygen supply, flame appearance, and product testing could resolve which group observed complete combustion.",
                    "answer_hint": "Complete combustion should be tied to greater oxygen supply, a bluer cleaner flame, and products dominated by CO2 and H2O; incomplete combustion may include CO or soot.",
                },
            ],
        },
        "lab_and_applications": {
            "multiple_choice": [
                {
                    "stem": "Which combination of evidence would be strongest for confirming that a clear acid spill has been neutralized rather than merely diluted?",
                    "options": [
                        "A. The solution is colorless and the volume increased",
                        "B. The pH is near neutral and reaction evidence is supported by a justified indicator or probe test",
                        "C. The beaker feels cool and no odor is noticed",
                        "D. The solution remains transparent and unstirred",
                    ],
                    "answer_hint": "B",
                },
                {
                    "stem": "Why is notation precision especially important when comparing two possible product predictions for the same reactants?",
                    "options": [
                        "A. Small notation differences can distinguish entirely different substances or states",
                        "B. Notation only affects the appearance of the answer",
                        "C. Correct notation removes the need to balance",
                        "D. State symbols matter only in physics labs",
                    ],
                    "answer_hint": "A",
                },
                {
                    "stem": "A burner flame becomes luminous orange during heating. Which explanation best links the observation to reaction conditions and likely products?",
                    "options": [
                        "A. More oxygen is entering, so only water is produced",
                        "B. Less oxygen is entering, so incomplete combustion becomes more likely",
                        "C. Combustion has stopped completely, so no products form",
                        "D. The gas is condensing, so a precipitation reaction begins",
                    ],
                    "answer_hint": "B",
                },
            ],
            "written_response": [
                {
                    "stem": "A student writes the correct products for a reaction but omits all state symbols. Explain how this can reduce scientific quality and give one situation where the missing state would change the interpretation of the reaction.",
                    "answer_hint": "A strong response should explain that state symbols communicate physical state and can indicate precipitation / gas formation; accept a justified example such as AgCl(s) versus AgCl(aq).",
                },
                {
                    "stem": "Describe a short test plan that would distinguish between a clear solution containing unreacted acid and a clear solution that has already been neutralized.",
                    "answer_hint": "Accept a valid plan using pH paper, an indicator, or a probe with expected acidic versus near-neutral results and appropriate safety reasoning.",
                },
            ],
            "application": [
                {
                    "stem": "Design a response to a lab partner who claims that 'no visible change means no chemical reaction.' Use at least two pieces of chemical evidence and one example from Unit 2 in your explanation.",
                    "answer_hint": "A strong response should reject the claim and use evidence such as pH change, temperature change, conductivity change, or gas detection, tied to a relevant Unit 2 example.",
                },
                {
                    "stem": "A class is comparing two methods for checking whether combustion in a burner is complete. Recommend the stronger method and justify your choice using both observation-based and chemical reasoning.",
                    "answer_hint": "A strong response should connect flame appearance, soot formation, and product reasoning to the recommended method and explain why the evidence is more reliable.",
                },
            ],
        },
    }
}

VARIANT_SUFFIXES: Dict[str, List[str]] = {
    "multiple_choice": [
        "",
        " Choose the best answer.",
        " Select the most accurate option.",
    ],
    "written_response": [
        "",
        " Show the essential steps clearly.",
        " Use appropriate notation in your response.",
    ],
    "application": [
        "",
        " Support your answer with clear reasoning.",
        " Use a real-world explanation where appropriate.",
    ],
    "short_answer": [
        "",
        " Keep your answer concise but precise.",
    ],
}
CHALLENGE_SUFFIXES: Dict[str, List[str]] = {
    "multiple_choice": [
        " Consider balancing, classification, and any evidence in the scenario before choosing.",
        " Focus on the chemically best-supported answer rather than the most familiar one.",
    ],
    "written_response": [
        " Justify each major step or classification in your response.",
        " Include enough chemistry reasoning to show why your answer is valid, not just what it is.",
    ],
    "application": [
        " Support your answer with chemical evidence and address one likely misconception.",
        " Connect your explanation to both reaction theory and real lab or real-world evidence.",
    ],
}
OPTION_LABELS = ["A", "B", "C", "D", "E", "F"]
OPTION_PREFIX_RE = re.compile(r"^\s*([A-Z])[\).]\s*(.*)$")


def infer_question_count(section_plan: Dict[str, Any]) -> int:
    explicit_num_questions = section_plan.get("num_questions")
    if isinstance(explicit_num_questions, int) and explicit_num_questions > 0:
        return explicit_num_questions

    explicit_count = section_plan.get("estimated_question_count")
    if isinstance(explicit_count, int) and explicit_count > 0:
        return explicit_count

    title = (section_plan.get("title") or "").lower()
    question_types = section_plan.get("question_types", []) or []
    marks = section_plan.get("marks")

    if "multiple choice" in title or "multiple_choice" in question_types:
        return 5
    if "application" in title or "application" in question_types:
        return 2
    if "written" in title or "written_response" in question_types:
        return 3

    if isinstance(marks, int) and marks > 0:
        return max(2, min(5, max(1, marks // 2)))

    return 3


def _default_marks_for_type(question_type: str) -> int:
    if question_type == "multiple_choice":
        return 1
    if question_type == "application":
        return 4
    if question_type == "short_answer":
        return 2
    return 3


def _normalize_question_type(question_type: str) -> str:
    value = (question_type or "").strip().lower()
    if value in {"multiple_choice", "application", "written_response", "short_answer"}:
        return value
    return "written_response"


def _choose_question_type(section_plan: Dict[str, Any], question_index: int) -> str:
    question_types = [
        _normalize_question_type(item)
        for item in (section_plan.get("question_types", []) or [])
    ]

    if question_types:
        return question_types[question_index % len(question_types)]

    response_formats = [
        _normalize_question_type(item)
        for item in (section_plan.get("response_formats", []) or [])
        if item
    ]

    if response_formats:
        return response_formats[question_index % len(response_formats)]

    return "written_response"


def _topic_for_question(section_plan: Dict[str, Any], question_index: int) -> str:
    topics = [item for item in (section_plan.get("target_topics", []) or []) if item]
    if not topics:
        return "general_content"
    return topics[question_index % len(topics)]


def _template_bank_for_subject(subject: str) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    return SUBJECT_TEMPLATE_BANKS.get(subject.strip().lower(), GENERIC_TEMPLATE_BANK)


def _stable_seed(*parts: Any) -> int:
    text = "|".join(str(part) for part in parts if part is not None)
    return sum(ord(ch) for ch in text)


def _template_signature(topic: str, question_type: str, template: Dict[str, Any]) -> str:
    return f"{topic}::{question_type}::{template.get('stem', '').strip()}"


def _template_candidates_for_topic(
    *,
    subject: str,
    topic: str,
    question_type: str,
    complexity_mode: str = "standard",
) -> List[Dict[str, Any]]:
    subject_bank = _template_bank_for_subject(subject)
    topic_bank = (
        subject_bank.get(topic)
        or subject_bank.get("general_content")
        or GENERIC_TEMPLATE_BANK["general_content"]
    )
    template_list = topic_bank.get(question_type)

    if not template_list:
        template_list = (
            topic_bank.get("written_response")
            or GENERIC_TEMPLATE_BANK["general_content"]["written_response"]
        )

    normalized_complexity = str(complexity_mode or "standard").strip().lower()
    if normalized_complexity not in {"challenging", "advanced", "hard"}:
        return template_list

    challenge_bank = CHALLENGING_TEMPLATE_BANKS.get(subject.strip().lower(), {})
    challenge_topic_bank = challenge_bank.get(topic) or challenge_bank.get("general_content") or {}
    challenge_templates = challenge_topic_bank.get(question_type) or []
    if not challenge_templates:
        return template_list

    return challenge_templates + template_list


def _has_unused_template(
    *,
    subject: str,
    topic: str,
    question_type: str,
    used_signatures: Optional[Set[str]],
    complexity_mode: str = "standard",
) -> bool:
    if used_signatures is None:
        return True

    for template in _template_candidates_for_topic(
        subject=subject,
        topic=topic,
        question_type=question_type,
        complexity_mode=complexity_mode,
    ):
        signature = _template_signature(topic, question_type, template)
        if signature not in used_signatures:
            return True

    return False


def _select_template(
    subject: str,
    topic: str,
    question_type: str,
    question_index: int,
    *,
    section_title: str,
    version_label: Optional[str],
    used_signatures: Optional[Set[str]] = None,
    complexity_mode: str = "standard",
) -> Dict[str, Any]:
    template_list = _template_candidates_for_topic(
        subject=subject,
        topic=topic,
        question_type=question_type,
        complexity_mode=complexity_mode,
    )
    lowered_title = section_title.strip().lower()
    if (
        subject.strip().lower() == "chemistry"
        and question_type == "application"
        and topic == "stoichiometry"
        and any(keyword in lowered_title for keyword in ("lab", "yield", "precipitate"))
    ):
        lab_templates = [
            template
            for template in template_list
            if any(
                keyword in str(template.get("stem", "")).lower()
                for keyword in ("yield", "precipitate", "filter paper", "agcl", "agno3")
            )
        ]
        if lab_templates:
            remaining_templates = [
                template for template in template_list if template not in lab_templates
            ]
            template_list = lab_templates + remaining_templates

    base_index = _stable_seed(
        subject,
        topic,
        question_type,
        section_title,
        version_label or "v1",
        question_index,
    ) % len(template_list)

    if used_signatures is None:
        return template_list[base_index]

    for offset in range(len(template_list)):
        candidate = template_list[(base_index + offset) % len(template_list)]
        signature = _template_signature(topic, question_type, candidate)
        if signature not in used_signatures:
            used_signatures.add(signature)
            return candidate

    chosen = template_list[base_index]
    used_signatures.add(_template_signature(topic, question_type, chosen))
    return chosen


def _apply_stem_variation(
    *,
    stem: str,
    question_type: str,
    question_number: int,
    section_title: str,
    version_label: Optional[str],
) -> str:
    suffixes = VARIANT_SUFFIXES.get(question_type, [""])
    suffix = suffixes[
        _stable_seed(question_type, question_number, section_title, version_label or "v1")
        % len(suffixes)
    ]

    if suffix and stem.endswith(suffix):
        return stem
    return stem + suffix


def _apply_complexity_variation(
    *,
    stem: str,
    answer_hint: Any,
    question_type: str,
    question_number: int,
    section_title: str,
    version_label: Optional[str],
    complexity_mode: str,
) -> tuple[str, Any]:
    normalized_complexity = str(complexity_mode or "standard").strip().lower()
    if normalized_complexity not in {"challenging", "advanced", "hard"}:
        return stem, answer_hint

    suffixes = CHALLENGE_SUFFIXES.get(question_type, [])
    if not suffixes:
        return stem, answer_hint

    suffix = suffixes[
        _stable_seed(
            "challenge",
            question_type,
            question_number,
            section_title,
            version_label or "v1",
        )
        % len(suffixes)
    ]
    varied_stem = stem if stem.endswith(suffix) else stem + suffix

    if not answer_hint:
        return varied_stem, answer_hint

    answer_hint_text = str(answer_hint).strip()
    if question_type == "multiple_choice":
        return varied_stem, answer_hint_text

    if "accept" in answer_hint_text.lower() or "strong response" in answer_hint_text.lower():
        answer_hint_text += " Reward clear chemical justification, not just the final statement."
    else:
        answer_hint_text += " Include a brief chemical justification."

    return varied_stem, answer_hint_text


def _parse_option(option: str, *, fallback_label: str) -> tuple[str, str]:
    match = OPTION_PREFIX_RE.match(option.strip())
    if match:
        return match.group(1), match.group(2).strip()
    return fallback_label, option.strip()


def _shuffle_multiple_choice_options(
    *,
    options: List[str],
    answer_hint: Any,
    question_number: int,
    section_title: str,
    version_label: Optional[str],
    stem: str,
) -> tuple[List[str], Any]:
    if not options:
        return options, answer_hint

    correct_label = str(answer_hint).strip().upper()
    if correct_label not in OPTION_LABELS:
        return options, answer_hint

    parsed = [
        _parse_option(option, fallback_label=OPTION_LABELS[idx % len(OPTION_LABELS)])
        for idx, option in enumerate(options)
    ]
    indexed = list(enumerate(parsed))

    indexed.sort(
        key=lambda item: _stable_seed(
            version_label or "v1",
            section_title,
            stem,
            question_number,
            item[0],
            item[1][1],
        )
    )

    remapped_options: List[str] = []
    remapped_answer = correct_label

    for new_index, (_, (old_label, option_text)) in enumerate(indexed):
        new_label = OPTION_LABELS[new_index]
        remapped_options.append(f"{new_label}. {option_text}")
        if old_label == correct_label:
            remapped_answer = new_label

    return remapped_options, remapped_answer


def _ground_stem_with_content(
    *,
    stem: str,
    question_type: str,
    snippet: Dict[str, Any] | None,
) -> str:
    if not snippet:
        return stem

    excerpt = str(snippet.get("excerpt") or "").strip()
    if not excerpt:
        return stem

    if question_type == "multiple_choice":
        return f"Unit-content idea: {excerpt}\n\n{stem}"
    if question_type == "application":
        return f"Use this unit-content idea in your answer: {excerpt}\n\n{stem}"
    return f"Based on the unit content: {excerpt}\n\n{stem}"


def build_question_record(
    *,
    subject: str,
    section_plan: Dict[str, Any],
    question_number: int,
    question_index: int,
    used_signatures: Optional[Set[str]] = None,
    version_label: Optional[str] = None,
) -> Dict[str, Any]:
    question_type = _choose_question_type(section_plan, question_index)
    topic = _topic_for_question(section_plan, question_index)
    section_title = section_plan.get("title") or "Section"
    complexity_mode = str(section_plan.get("complexity_mode") or "standard")
    candidate_topics = [item for item in (section_plan.get("target_topics", []) or []) if item]

    if candidate_topics and used_signatures:
        start_index = question_index % len(candidate_topics)
        rotated_topics = candidate_topics[start_index:] + candidate_topics[:start_index]
        for candidate_topic in rotated_topics:
            if _has_unused_template(
                subject=subject,
                topic=candidate_topic,
                question_type=question_type,
                used_signatures=used_signatures,
                complexity_mode=complexity_mode,
            ):
                topic = candidate_topic
                break

    template = _select_template(
        subject,
        topic,
        question_type,
        question_index,
        section_title=section_title,
        version_label=version_label,
        used_signatures=used_signatures,
        complexity_mode=complexity_mode,
    )

    varied_stem = _apply_stem_variation(
        stem=template["stem"],
        question_type=question_type,
        question_number=question_number,
        section_title=section_title,
        version_label=version_label,
    )
    source_snippets = section_plan.get("source_snippets", []) or []
    source_snippet = (
        source_snippets[question_index % len(source_snippets)]
        if source_snippets
        else None
    )
    varied_stem = _ground_stem_with_content(
        stem=varied_stem,
        question_type=question_type,
        snippet=source_snippet,
    )
    options = template.get("options", [])
    answer_hint = template.get("answer_hint")
    varied_stem, answer_hint = _apply_complexity_variation(
        stem=varied_stem,
        answer_hint=answer_hint,
        question_type=question_type,
        question_number=question_number,
        section_title=section_title,
        version_label=version_label,
        complexity_mode=complexity_mode,
    )

    if question_type == "multiple_choice":
        options, answer_hint = _shuffle_multiple_choice_options(
            options=options,
            answer_hint=answer_hint,
            question_number=question_number,
            section_title=section_title,
            version_label=version_label,
            stem=varied_stem,
        )

    configured_marks = section_plan.get("question_marks") or []
    marks = _default_marks_for_type(question_type)
    if question_index < len(configured_marks):
        try:
            configured_mark = int(configured_marks[question_index])
        except (TypeError, ValueError):
            configured_mark = 0
        if configured_mark > 0:
            marks = configured_mark

    return {
        "question_number": question_number,
        "topic": topic,
        "question_type": question_type,
        "marks": marks,
        "stem": varied_stem,
        "options": options,
        "answer_hint": answer_hint,
        "source_excerpt": source_snippet.get("excerpt") if source_snippet else None,
    }


def _render_question_markdown(question: Dict[str, Any]) -> str:
    lines = [
        f"{question['question_number']}. {question['stem']} ({question['marks']} mark{'s' if question['marks'] != 1 else ''})"
    ]

    options = question.get("options", []) or []
    if options:
        for option in options:
            lines.append(f"   {option}")

    return "\n".join(lines)


def _normalize_prebuilt_question(
    *,
    question: Dict[str, Any],
    question_number: int,
    section_plan: Dict[str, Any],
) -> Dict[str, Any]:
    question_type = _normalize_question_type(
        str(question.get("question_type") or question.get("type") or "")
    )
    if question_type == "written_response":
        question_type = _choose_question_type(section_plan, 0)

    marks = question.get("marks")
    try:
        marks = int(marks)
    except (TypeError, ValueError):
        marks = _default_marks_for_type(question_type)

    options = question.get("options") or []
    if question_type != "multiple_choice":
        options = []

    return {
        "question_number": question_number,
        "topic": str(
            question.get("topic")
            or _topic_for_question(section_plan, max(0, question_number - 1))
        ),
        "question_type": question_type,
        "marks": marks,
        "stem": str(question.get("stem") or "").strip(),
        "options": [str(option).strip() for option in options if str(option).strip()],
        "answer_hint": question.get("answer_hint"),
        "source_excerpt": question.get("source_excerpt"),
    }


def render_section(
    *,
    subject: str,
    section_plan: Dict[str, Any],
    start_question_number: int,
    used_signatures: Optional[Set[str]] = None,
    version_label: Optional[str] = None,
) -> Dict[str, Any]:
    question_count = infer_question_count(section_plan)
    questions: List[Dict[str, Any]] = []
    markdown_parts: List[str] = []

    section_title = section_plan.get("title") or "Section"
    markdown_parts.append(f"## {section_title}")

    section_meta: List[str] = []
    question_count_label = infer_question_count(section_plan)
    marks = section_plan.get("marks")
    instructions = section_plan.get("instructions")
    timing_notes = section_plan.get("timing_notes")

    if question_count_label or marks:
        details: List[str] = []
        if question_count_label:
            details.append(
                f"{question_count_label} question{'s' if question_count_label != 1 else ''}"
            )
        if isinstance(marks, int) and marks > 0:
            details.append(f"{marks} marks")
        if details:
            section_meta.append(f"*Section Plan: {' | '.join(details)}*")

    if instructions:
        section_meta.append(f"*Instructions: {instructions}*")

    if timing_notes:
        section_meta.append(f"*Timing Notes: {timing_notes}*")

    if section_meta:
        markdown_parts.extend(section_meta)

    current_number = start_question_number

    prebuilt_questions = section_plan.get("prebuilt_questions") or []
    if prebuilt_questions:
        for item in prebuilt_questions[:question_count]:
            question = _normalize_prebuilt_question(
                question=item,
                question_number=current_number,
                section_plan=section_plan,
            )
            questions.append(question)
            markdown_parts.append(_render_question_markdown(question))
            current_number += 1
    else:
        for idx in range(question_count):
            question = build_question_record(
                subject=subject,
                section_plan=section_plan,
                question_number=current_number,
                question_index=idx,
                used_signatures=used_signatures,
                version_label=version_label,
            )
            questions.append(question)
            markdown_parts.append(_render_question_markdown(question))
            current_number += 1

    return {
        "section_title": section_title,
        "questions": questions,
        "markdown": "\n\n".join(markdown_parts),
        "next_question_number": current_number,
    }
