import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

interface Map {
  django_id:number;
  map_title:string;
  map_maker:string;
  map_year:string;
  image:string;
}

function App() {
  const [mapArray, setMaps] = useState<Map[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/maps/')
    .then(response => response.json())
    .then(data => {
      setMaps(data);
      setLoading(false)
    })
    .catch(error => {
      console.error('Couldnt fetch maps:', error);
      setLoading(false);
    });
  }, []//run only once
  );

  if(loading){
    return <div>Loading Maps</div>;
  } 

  return (
    <div className="App">
        <h1>Map Collection</h1>
        <div className="map-grid">
          {mapArray.map((mapInstance) => (
            <div key={mapInstance.django_id} className="map-entry">
              <h3>{mapInstance.map_title}</h3>
              <p>Maker: {mapInstance.map_maker}</p>
              <p>Year: {mapInstance.map_year}</p>
              {mapInstance.image && (
                <img src={`http://localhost:8000${mapInstance.image}`} alt={mapInstance.map_title} />
              )}
            </div>
         ))}
        </div>
    </div>
  )
}

export default App
