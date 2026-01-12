import React, { useEffect, useState } from 'react';
import styles from './MapGallery.module.css';

interface Map {
  django_id:number;
  map_title:string;
  map_maker:string;
  map_year:string;
  image:string;
}

function MapGallery() {
  const [mapArray, setMaps] = useState<Map[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/maps/')
    .then(response => response.json())
    .then(data => {
      console.log(data);
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
    <div className={"App"}>
        <h1>Map Collection</h1>
        <div className={styles.mapGrid}>
          {mapArray.map((mapInstance) => (
            <div key={mapInstance.django_id} className={styles.mapInstance}>
              <h3 className={styles.mapTitle}>{mapInstance.map_title}</h3>
              <p className={styles.mapDetails}>Maker: {mapInstance.map_maker}</p>
              <p className={styles.mapDetails}>Year: {mapInstance.map_year}</p>
              {mapInstance.image && (
                <img src={mapInstance.image} alt={mapInstance.map_title} className={styles.mapImage}/>
              )}
            </div>
         ))}
        </div>
    </div>
  )
}

export default MapGallery