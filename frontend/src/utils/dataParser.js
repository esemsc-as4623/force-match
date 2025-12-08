// Data parser utility for TTL files
import { Parser } from 'n3';

export const parseCharactersFromTTL = async (ttlContent) => {
  return new Promise((resolve, reject) => {
    const parser = new Parser();
    const characters = new Map();
    
    try {
      const quads = parser.parse(ttlContent);
      
      quads.forEach(quad => {
        const subject = quad.subject.value;
        const predicate = quad.predicate.value;
        const object = quad.object.value;
        
        // Check if this is a character
        if (predicate === 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' && 
            object === 'https://swapi.co/vocabulary/Character') {
          if (!characters.has(subject)) {
            characters.set(subject, { 
              id: subject,
              name: '',
              type: '',
              species: '',
              gender: '',
              homeworld: '',
              height: '',
              mass: '',
              hairColor: '',
              skinColor: '',
              eyeColor: '',
              birthYear: '',
              films: []
            });
          }
        }
        
        // Extract character properties
        if (characters.has(subject)) {
          const char = characters.get(subject);
          
          switch(predicate) {
            case 'http://www.w3.org/2000/01/rdf-schema#label':
              char.name = object;
              break;
            case 'http://www.ontotext.com/business-object/type':
              char.type = object;
              char.species = object;
              break;
            case 'https://swapi.co/vocabulary/gender':
              char.gender = object;
              break;
            case 'https://swapi.co/vocabulary/homeworld':
              char.homeworld = object;
              break;
            case 'https://swapi.co/vocabulary/height':
              char.height = object;
              break;
            case 'https://swapi.co/vocabulary/mass':
              char.mass = object;
              break;
            case 'https://swapi.co/vocabulary/hairColor':
              char.hairColor = object;
              break;
            case 'https://swapi.co/vocabulary/skinColor':
              char.skinColor = object;
              break;
            case 'https://swapi.co/vocabulary/eyeColor':
              char.eyeColor = object;
              break;
            case 'https://swapi.co/vocabulary/birthYear':
              char.birthYear = object;
              break;
            case 'https://swapi.co/vocabulary/film':
              if (!char.films.includes(object)) {
                char.films.push(object);
              }
              break;
          }
        }
      });
      
      resolve(Array.from(characters.values()));
    } catch (error) {
      reject(error);
    }
  });
};

export const parseConnectionsFromTTL = async (ttlContent) => {
  return new Promise((resolve, reject) => {
    const parser = new Parser();
    const connections = [];
    
    try {
      const quads = parser.parse(ttlContent);
      
      quads.forEach(quad => {
        const subject = quad.subject.value;
        const predicate = quad.predicate.value;
        const object = quad.object.value;
        
        if (predicate === 'https://swapi.co/vocabulary/connectedTo') {
          connections.push({
            source: subject,
            target: object
          });
        }
      });
      
      resolve(connections);
    } catch (error) {
      reject(error);
    }
  });
};

export const getColorForSpecies = (species) => {
  const colors = {
    'Human': '#4A9EFF',      // Blue
    'Droid': '#B270FF',      // Purple
    'Wookiee': '#FFE66D',    // Yellow
    'Rodian': '#7FFF00',     // Green
    'Hutt': '#FF8C42',       // Orange
    'Yoda\'s species': '#7FFF00', // Green
    'Trandoshan': '#FF3B3B', // Red
    'Mon Calamari': '#4A9EFF', // Blue
    'Ewok': '#FFE66D',       // Yellow
    'Sullustan': '#FF8C42',  // Orange
    'Neimodian': '#7FFF00',  // Green
    'Gungan': '#4A9EFF',     // Blue
    'Toydarian': '#B270FF',  // Purple
    'Dug': '#FF3B3B',        // Red
    'Twi\'lek': '#B270FF',   // Purple
    'Aleena': '#FF8C42',     // Orange
    'Vulptereen': '#FFE66D', // Yellow
    'Xexto': '#7FFF00',      // Green
    'Toong': '#4A9EFF',      // Blue
    'Cerean': '#B270FF',     // Purple
    'Nautolan': '#4A9EFF',   // Blue
    'Zabrak': '#FF3B3B',     // Red
    'Tholothian': '#B270FF', // Purple
    'Iktotchi': '#FF8C42',   // Orange
    'Quermian': '#7FFF00',   // Green
    'Kel Dor': '#4A9EFF',    // Blue
    'Chagrian': '#B270FF',   // Purple
    'Geonosian': '#FF3B3B',  // Red
    'Mirialan': '#7FFF00',   // Green
    'Clawdite': '#B270FF',   // Purple
    'Besalisk': '#FF8C42',   // Orange
    'Kaminoan': '#4A9EFF',   // Blue
    'Skakoan': '#FFE66D',    // Yellow
    'Muun': '#B270FF',       // Purple
    'Togruta': '#FF3B3B',    // Red
    'Kaleesh': '#FF8C42',    // Orange
    'Pau\'an': '#B270FF',    // Purple
  };
  
  return colors[species] || '#4A9EFF';
};
