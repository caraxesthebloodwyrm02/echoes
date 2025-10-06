import React, { useState } from 'react';
import { ChevronRight, Book, Eye, Brain, Heart, Crown, Shield, Zap, Moon, Sun, Star, Users } from 'lucide-react';

const HarryPotterDeepDive = () => {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedInsight, setSelectedInsight] = useState(null);

  const categories = {
    characters: {
      icon: <Users className="w-6 h-6" />,
      title: "Character Psychology",
      subtitle: "Beyond the Surface",
      color: "bg-red-600",
      insights: {
        snape: {
          title: "Severus Snape: The Unreliable Narrator's Shadow",
          book_context: "From Harry's limited POV, we miss Snape's true complexity",
          deep_insight: {
            psychological: "Snape embodies the 'wounded healer' archetype - his cruelty stems from unprocessed trauma. His teaching method, while harsh, mirrors how trauma survivors often unconsciously recreate their own painful experiences.",
            missed_nuance: "The books reveal Snape's working-class background through subtle details: his worn clothes, his father's abandonment, his mother's magical heritage being looked down upon. His resentment isn't just about Lily - it's about class, belonging, and never being 'enough.'",
            literary_device: "Rowling uses Snape to explore how perspectives shape reality. Harry's hatred blinds him to Snape's protection until the very end - a masterclass in unreliable narration.",
            moral_complexity: "Snape's 'redemption' isn't clean. He remains cruel to children throughout. His love for Lily is possessive, not pure. He's neither hero nor villain but devastatingly human."
          },
          film_vs_book: "Alan Rickman's portrayal, while iconic, softened Snape's edges. Book-Snape is far more viscerally cruel, making his ultimate sacrifice more shocking and complex."
        },
        dumbledore: {
          title: "Albus Dumbledore: The Burden of Omniscience",
          book_context: "The gradual revelation of Dumbledore's fallibility across books 4-7",
          deep_insight: {
            psychological: "Dumbledore represents the 'wise fool' - his greatest wisdom comes from his greatest mistakes. His relationship with Grindelwald reveals how idealism can corrupt, and how guilt can drive decades of overcorrection.",
            missed_nuance: "Dumbledore's treatment of Harry as a 'horcrux weapon' is deeply problematic when examined closely. He withholds crucial information repeatedly, making Harry complicit in his own potential death without informed consent.",
            literary_device: "His character arc mirrors the loss of childhood faith in authority. Parents aren't perfect; mentors aren't omniscient. Growing up means accepting that even our heroes are deeply flawed.",
            moral_complexity: "His 'greater good' philosophy led him to sacrifice individuals for the collective - exactly what he fought against in Grindelwald. The irony is intentional and devastating."
          },
          film_vs_book: "Films focus on grandfatherly warmth. Books reveal a manipulative strategist whose kindness often serves larger, hidden purposes."
        },
        voldemort: {
          title: "Tom Riddle: The Banality of Evil",
          book_context: "The memories in Book 6 show evil's mundane origins",
          deep_insight: {
            psychological: "Voldemort isn't born evil - he's created by abandonment, institutional failure, and the gradual erosion of empathy. His inability to love isn't mystical; it's the result of severe attachment trauma.",
            missed_nuance: "The Gaunt family memories reveal how poverty, inbreeding, and generational trauma create monsters. Tom's mother dies not from a broken heart, but from giving up her will to live - a form of magical depression that mirrors real-world maternal mortality in desperate circumstances.",
            literary_device: "Splitting his soul through horcruxes is a perfect metaphor for how evil fragments the self. Each murder makes him less human, not more powerful.",
            moral_complexity: "Young Tom's charisma and intelligence make him sympathetic until you realize he's already manipulating and hurting others. Evil often comes wrapped in charm and capability."
          },
          film_vs_book: "Films make Voldemort a generic monster. Books show how ordinary cruelty and neglect create extraordinary evil."
        },
        hermione: {
          title: "Hermione Granger: The Price of Perfection",
          book_context: "Her character flaws and growth throughout the series",
          deep_insight: {
            psychological: "Hermione exhibits classic traits of gifted child syndrome - perfectionism, anxiety, and difficulty with criticism. Her rule-following masks deep insecurity about belonging in the wizarding world.",
            missed_nuance: "Her treatment of house-elves (S.P.E.W.) reveals both admirable activism and problematic saviorism. She assumes she knows what's best without listening to those she's trying to help - a common trap for well-meaning allies.",
            literary_device: "She represents the 'outsider's perspective' - muggle-born, she sees wizarding world problems that magical people are blind to, but also misses cultural nuances.",
            moral_complexity: "Her memory-modification of her parents is profoundly disturbing when examined closely. She removes herself from their lives without consent, essentially 'killing' their daughter to protect them."
          },
          film_vs_book: "Films smooth out her more abrasive qualities. Book-Hermione can be self-righteous, condescending, and occasionally cruel when her worldview is challenged."
        }
      }
    },
    themes: {
      icon: <Brain className="w-6 h-6" />,
      title: "Hidden Themes",
      subtitle: "What Rowling Really Wrote About",
      color: "bg-blue-600",
      insights: {
        power: {
          title: "Power Corrupts - Even the Good Guys",
          book_context: "Ministry corruption, Dumbledore's manipulation, Harry's temptations",
          deep_insight: {
            psychological: "Every character with power - Dumbledore, Fudge, Scrimgeour, even Harry - makes morally questionable choices. Power doesn't corrupt; it reveals who people really are under pressure.",
            missed_nuance: "The series consistently shows that institutional power is inherently corrupting. The Ministry, Hogwarts, even the Order of the Phoenix make decisions that prioritize their existence over individual welfare.",
            literary_device: "Harry's temptation to use Unforgivable Curses shows how thin the line is between hero and villain. He successfully uses Imperio and tries to use Cruciatus - the 'good guys' aren't above dark magic when pushed.",
            moral_complexity: "The series asks: Is it okay to lie, manipulate, and sacrifice individuals if it serves a greater good? Dumbledore says yes; the story suggests it's more complicated."
          },
          film_vs_book: "Films present clearer moral lines. Books show how circumstances force good people into morally gray territories."
        },
        prejudice: {
          title: "Systemic Oppression and Complicity",
          book_context: "House-elf slavery, muggle-born persecution, werewolf discrimination",
          deep_insight: {
            psychological: "The wizarding world's treatment of non-human magical beings mirrors real-world systemic oppression. Most 'good' characters are complicit through inaction or willful ignorance.",
            missed_nuance: "House-elf enslavement isn't just background detail - it's a functioning economic system that even progressive characters like the Weasleys participate in without question. Only Hermione (the outsider) sees it clearly.",
            literary_device: "Rowling uses magical prejudice to explore how oppression functions: through legal systems (werewolf registration), economic control (goblin banking restrictions), and cultural normalization (house-elf 'happiness' in servitude).",
            moral_complexity: "The 'good guys' win but don't fundamentally change the system. Harry becomes an Auror - joining the same institution that enforced discriminatory laws. Reform, not revolution."
          },
          film_vs_book: "Films largely ignore systemic issues, focusing on individual villains rather than institutional problems."
        },
        death: {
          title: "Death as Transformation, Not Ending",
          book_context: "The progression from fearing death to accepting it across the series",
          deep_insight: {
            psychological: "Harry's relationship with death evolves from terror (book 1) to acceptance (book 7). This mirrors the psychological stages of grief and the process of maturation.",
            missed_nuance: "The Resurrection Stone doesn't bring back the dead - it shows echoes of love that persist. Harry's parents, Sirius, and Lupin aren't really there; they're manifestations of Harry's internalized relationships with them.",
            literary_device: "Each book features a different aspect of death: mystery (Stone), memory (Chamber), innocence (Prisoner), return (Goblet), denial (Phoenix), acceptance (Prince), transcendence (Hallows).",
            moral_complexity: "Harry's willingness to die isn't suicidal - it's the ultimate expression of love. But the story also shows how the death of loved ones can drive people to desperate, destructive acts (Snape, Voldemort's mother)."
          },
          film_vs_book: "Films focus on action and spectacle. Books explore death as a philosophical and emotional journey."
        }
      }
    },
    symbolism: {
      icon: <Eye className="w-6 h-6" />,
      title: "Hidden Symbolism",
      subtitle: "The Deeper Meanings",
      color: "bg-purple-600",
      insights: {
        mirrors: {
          title: "Mirrors: Reflection and Self-Knowledge",
          book_context: "Mirror of Erised, two-way mirror, broken mirrors throughout",
          deep_insight: {
            psychological: "Mirrors consistently represent the gap between reality and desire, truth and fantasy. Harry's journey is about learning to see himself clearly rather than through others' expectations or his own fantasies.",
            missed_nuance: "The Mirror of Erised shows 'the deepest desire of our hearts' - but Harry's vision of his family isn't just wishful thinking. It's his unconscious recognition that love, not fame, is what makes life meaningful.",
            literary_device: "Broken mirrors appear throughout the series (Sirius's gift, the shard that saves Harry) - suggesting that sometimes broken perspectives reveal more truth than perfect ones.",
            moral_complexity: "The mirror can drive people mad with longing. Harry's ability to walk away from it in book 1 foreshadows his ability to walk to his death in book 7 - both require choosing reality over fantasy."
          },
          film_vs_book: "Films use mirrors as plot devices. Books use them as windows into character psychology and theme."
        },
        names: {
          title: "The Power of Names",
          book_context: "Fear of Voldemort's name, true names vs. chosen names",
          deep_insight: {
            psychological: "Names have power because they represent identity and relationship. Refusing to say 'Voldemort' isn't just fear - it's a form of magical thinking that gives the name power over the speaker.",
            missed_nuance: "Tom Riddle's rejection of his name represents his rejection of his humanity. Creating 'Lord Voldemort' is his attempt to recreate himself without vulnerability or connection.",
            literary_device: "Characters' relationships are revealed through what they call each other: Harry calls Snape 'Professor' even after learning the truth, showing respect despite everything.",
            moral_complexity: "Harry names his son 'Severus' - a controversial choice that suggests either forgiveness or a fundamental misunderstanding of who Snape really was."
          },
          film_vs_book: "Films simplify the name taboo. Books explore how language shapes reality and relationships."
        },
        houses: {
          title: "Houses as Internal Conflict",
          book_context: "The Sorting Hat's struggles, Harry's Slytherin qualities",
          deep_insight: {
            psychological: "The houses don't just categorize students - they represent internal psychological tensions that exist within individuals. Harry embodies all four houses at different times.",
            missed_nuance: "The Sorting Hat's difficulty placing certain students (Harry, Hermione, Neville) suggests that personal growth requires integrating different aspects of personality, not choosing just one.",
            literary_device: "House stereotypes are consistently subverted: brave Hufflepuffs, clever Gryffindors, loyal Slytherins, ambitious Ravenclaws. The categories are more fluid than they appear.",
            moral_complexity: "The house system perpetuates division and prejudice, yet also provides identity and belonging. It's both harmful and necessary - like many social institutions."
          },
          film_vs_book: "Films present houses as simple character categories. Books show them as complex, evolving aspects of identity."
        }
      }
    },
    foreshadowing: {
      icon: <Star className="w-6 h-6" />,
      title: "Masterful Foreshadowing",
      subtitle: "Clues Hidden in Plain Sight",
      color: "bg-green-600",
      insights: {
        horcruxes: {
          title: "The Horcrux Trail: Clues from Book 1",
          book_context: "Every horcrux is introduced before being revealed as one",
          deep_insight: {
            psychological: "The horcruxes represent different aspects of Voldemort's fractured psyche. Each one he made marked a further step away from humanity.",
            missed_nuance: "Harry's scar hurting isn't just a warning system - it's the horcrux in him resonating with Voldemort's emotions. Harry experiences fragments of Tom Riddle's broken soul throughout the series.",
            literary_device: "Rowling plants each horcrux in earlier books: Tom Riddle's diary (book 2), the locket and ring (book 6 memories), Hufflepuff's cup (mentioned in book 4), the diadem (Harry sees it in book 6), Nagini (present from book 4).",
            moral_complexity: "Destroying horcruxes means destroying pieces of a human soul. The act of creation is evil, but the destruction raises questions about the possibility of redemption vs. the necessity of justice."
          },
          film_vs_book: "Films compress the horcrux hunt. Books show how each discovery builds understanding of Voldemort's psychology and methods."
        },
        snape_clues: {
          title: "Snape's True Loyalty: Hidden in Every Book",
          book_context: "Subtle hints about Snape's protection of Harry throughout",
          deep_insight: {
            psychological: "Snape's behavior towards Harry is consistently protective disguised as hostility. His cruelty serves to maintain his cover while still keeping Harry safe.",
            missed_nuance: "Snape's knowledge of Harry's location, his interventions during Quidditch matches, his attempts to teach Harry Occlumency - all serve dual purposes that become clear only in retrospect.",
            literary_device: "Rowling uses dramatic irony masterfully - readers suspect Snape of evil while he's actually performing the most heroic acts in the series.",
            moral_complexity: "Snape's protection of Harry doesn't excuse his abuse of other students. He can be simultaneously heroic and cruel, loving and petty."
          },
          film_vs_book: "Films hint at Snape's complexity. Books provide a trail of evidence that completely recontextualizes his every action."
        },
        political_corruption: {
          title: "Ministry Corruption: Seeds Planted Early",
          book_context: "The progression from incompetence to active evil",
          deep_insight: {
            psychological: "The Ministry's evolution from bureaucratic bumbling to authoritarian control mirrors how democratic institutions can be corrupted from within.",
            missed_nuance: "Fudge's denial of Voldemort's return isn't just stubbornness - it's a politician prioritizing his career over public safety. The personal becomes political becomes catastrophic.",
            literary_device: "Each book shows the Ministry failing in different ways: incompetence (book 1), prejudice (book 2), corruption (book 3), denial (book 5), propaganda (book 6), totalitarianism (book 7).",
            moral_complexity: "Even 'good' Ministry employees like Arthur Weasley are complicit in a system that oppresses magical creatures and maintains unjust hierarchies."
          },
          film_vs_book: "Films simplify political themes. Books show how institutional corruption develops gradually and with the complicity of ordinary people."
        }
      }
    }
  };

  const resetSelection = () => {
    setSelectedCategory(null);
    setSelectedInsight(null);
  };

  if (selectedInsight) {
    const category = categories[selectedCategory];
    const insight = category.insights[selectedInsight];
    
    return (
      <div className="max-w-5xl mx-auto p-6 bg-gradient-to-br from-amber-50 to-purple-50 min-h-screen">
        <div className="mb-6">
          <button 
            onClick={resetSelection}
            className="flex items-center text-purple-700 hover:text-purple-900 mb-4"
          >
            <ChevronRight className="w-4 h-4 rotate-180 mr-2" />
            Back to {category.title}
          </button>
          
          <div className="bg-white rounded-lg shadow-xl p-8">
            <div className="flex items-center mb-6">
              {category.icon}
              <h2 className="text-3xl font-bold ml-3 text-gray-800">{insight.title}</h2>
            </div>
            
            <div className="bg-amber-50 p-4 rounded-lg mb-6">
              <h3 className="font-semibold text-amber-800 mb-2">Book Context</h3>
              <p className="text-amber-700">{insight.book_context}</p>
            </div>
            
            <div className="grid lg:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div className="bg-blue-50 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-blue-800 mb-3 flex items-center">
                    <Brain className="w-5 h-5 mr-2" />
                    Psychological Depth
                  </h3>
                  <p className="text-blue-700">{insight.deep_insight.psychological}</p>
                </div>
                
                <div className="bg-green-50 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-green-800 mb-3 flex items-center">
                    <Eye className="w-5 h-5 mr-2" />
                    Missed Nuance
                  </h3>
                  <p className="text-green-700">{insight.deep_insight.missed_nuance}</p>
                </div>
              </div>
              
              <div className="space-y-6">
                <div className="bg-purple-50 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-purple-800 mb-3 flex items-center">
                    <Book className="w-5 h-5 mr-2" />
                    Literary Device
                  </h3>
                  <p className="text-purple-700">{insight.deep_insight.literary_device}</p>
                </div>
                
                <div className="bg-red-50 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-red-800 mb-3 flex items-center">
                    <Heart className="w-5 h-5 mr-2" />
                    Moral Complexity
                  </h3>
                  <p className="text-red-700">{insight.deep_insight.moral_complexity}</p>
                </div>
              </div>
            </div>
            
            <div className="mt-8 bg-gradient-to-r from-gray-100 to-gray-200 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
                <Zap className="w-5 h-5 mr-2" />
                Film vs. Book
              </h3>
              <p className="text-gray-700">{insight.film_vs_book}</p>
            </div>
            
            <div className="mt-8 bg-gradient-to-r from-indigo-100 to-blue-100 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-indigo-800 mb-3">For Deeper Reflection</h3>
              <div className="space-y-2 text-indigo-700">
                <p>• How does this insight change your understanding of the character or theme?</p>
                <p>• What real-world parallels can you draw from this aspect of the story?</p>
                <p>• How might this deeper reading influence how you approach the books on a re-read?</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (selectedCategory) {
    const category = categories[selectedCategory];
    return (
      <div className="max-w-5xl mx-auto p-6 bg-gradient-to-br from-amber-50 to-purple-50 min-h-screen">
        <div className="mb-6">
          <button 
            onClick={() => setSelectedCategory(null)}
            className="flex items-center text-purple-700 hover:text-purple-900 mb-4"
          >
            <ChevronRight className="w-4 h-4 rotate-180 mr-2" />
            Back to All Categories
          </button>
          
          <div className="text-center mb-8">
            <div className={`inline-flex items-center justify-center w-16 h-16 ${category.color} text-white rounded-full mb-4`}>
              {category.icon}
            </div>
            <h2 className="text-3xl font-bold text-gray-800">{category.title}</h2>
            <p className="text-gray-600 text-lg">{category.subtitle}</p>
          </div>
        </div>
        
        <div className="grid gap-6">
          {Object.entries(category.insights).map(([key, insight]) => (
            <div 
              key={key}
              onClick={() => setSelectedInsight(key)}
              className="bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-all hover:scale-102"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-800 mb-2">{insight.title}</h3>
                  <p className="text-gray-600 mb-3">{insight.book_context}</p>
                  <div className="bg-gradient-to-r from-amber-50 to-purple-50 p-3 rounded">
                    <p className="text-sm text-gray-700">{insight.deep_insight.psychological.substring(0, 120)}...</p>
                  </div>
                </div>
                <ChevronRight className="w-6 h-6 text-gray-400 ml-4" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto p-6 bg-gradient-to-br from-amber-50 to-purple-50 min-h-screen">
      <div className="text-center mb-12">
        <div className="flex items-center justify-center mb-6">
          <Book className="w-12 h-12 text-purple-600 mr-4" />
          <h1 className="text-4xl font-bold text-gray-800">Harry Potter: Hidden Depths</h1>
        </div>
        <p className="text-gray-600 text-lg max-w-3xl mx-auto">
          Discover the psychological complexity, moral nuance, and literary brilliance that makes Harry Potter 
          a masterpiece of modern literature. These are the insights that the films couldn't capture and that 
          most readers miss on their first journey through the wizarding world.
        </p>
      </div>
      
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Object.entries(categories).map(([key, category]) => (
          <div 
            key={key}
            onClick={() => setSelectedCategory(key)}
            className="bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-all hover:scale-105"
          >
            <div className={`inline-flex items-center justify-center w-12 h-12 ${category.color} text-white rounded-full mb-4`}>
              {category.icon}
            </div>
            
            <h2 className="text-xl font-bold text-gray-800 mb-2">{category.title}</h2>
            <p className="text-gray-600 mb-4">{category.subtitle}</p>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">
                {Object.keys(category.insights).length} deep insights
              </span>
              <ChevronRight className="w-4 h-4 text-gray-400" />
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-12 bg-gradient-to-r from-purple-100 to-indigo-100 p-8 rounded-lg">
        <div className="flex items-center mb-4">
          <Moon className="w-6 h-6 text-indigo-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-800">Why These Insights Matter</h3>
        </div>
        <p className="text-gray-700 leading-relaxed mb-4">
          J.K. Rowling crafted a series that works on multiple levels - as children's adventure stories and as profound 
          explorations of human nature, power, love, and mortality. The deeper you dig, the more you discover how 
          intentionally she wove psychological truth and moral complexity into every character and theme.
        </p>
        <p className="text-gray-700 leading-relaxed">
          These insights reveal why Harry Potter continues to resonate with readers decades later. It's not just magic 
          and adventure - it's a mirror reflecting our own struggles with identity, belonging, power, and the choice 
          between love and fear that defines every human life.
        </p>
      </div>
    </div>
  );
};

export default HarryPotterDeepDive;