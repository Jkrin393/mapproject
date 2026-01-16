import React, { useEffect, useState } from 'react';
import styles from './MapGallery.module.css';

interface Map {
  id: number;
  external_map_id: number | null;
  map_maker: string;
  map_year: string;
  map_height: number | null;
  map_width: number | null;
  map_title: string;
  description: string;
  map_price: string;
  map_info_memo: string;
  planned_use: string;
  physical_location: string;
  image: string | null;
  upload_date: string;
  last_edit_date: string;
  collection: number | null;
  tags: number[];
}

interface PaginatedMapResponse {
  count: number;
  next: string|null;
  previous: string|null;
  results: Map[];
}

function MapGallery() {
  const API_BASE=import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  const [mapArray, setMaps] = useState<Map[]>([]);
  const [loading, setLoading] = useState(true);
  const [nextPage, setNextPage] = useState<string | null>(null);
  const [prevPage, setPrevPage] = useState<string | null>(null);

  //***********django returns paginated results
  useEffect(() => {
    fetch(`${API_BASE}/api/maps/`)
      .then(response => 
      {
        if (!response.ok) 
        {
          throw new Error(`HTTP error with status: ${response.status}`);
        }
        return response.json();
      })
    .then((data: PaginatedMapResponse) => 
      {
      console.log('response from API: ', data);
      console.log('array?', Array.isArray(data));
      console.log('results?', data.results);
      //const mapsArray=(data.results || data);
      //console.log('maps array: ', mapsArray);
      if(data.results && Array.isArray(data.results))
      {
        setMaps(data.results);
        setNextPage(data.next);
        setPrevPage(data.previous);
      } else
      {
        throw new Error('invalid data or structure from endpoint');
      }
      setLoading(false)
      })
    .catch(error => {
      console.error('Couldnt fetch maps:', error);
      setLoading(false);
    });
  }, [API_BASE]//run only once
  );

  if(loading){
    return <div>Loading Maps</div>;
  }

  if (!mapArray || mapArray.length === 0) 
  {
    return (
      <div className="empty">
        <h2>No maps found</h2>
        <p>Add some maps through the Django admin panel.</p>
      </div>
    );
  }
    // Helper function to get full image URL
  const getImageUrl = (imageUrl: string | null): string | null => {
    if (!imageUrl) return null;
    if (imageUrl.startsWith('http')) {
      return imageUrl;
    }
    return `${API_BASE}${imageUrl}`;
  };

  
  return (
    <div className={"App"}>
        <h1>Map Collection</h1>
        <div className={styles.mapGrid}>
          {mapArray.map((mapInstance) => (
            <div key={mapInstance.id} className={styles.mapInstance}>
              <h3 className={styles.mapTitle}>{mapInstance.map_title}</h3>
              <p className={styles.mapDetails}>Maker: {mapInstance.map_maker}</p>
              <p className={styles.mapDetails}>Year: {mapInstance.map_year}</p>
              {mapInstance.image && (
                <img src={getImageUrl(mapInstance.image)!} alt={mapInstance.map_title} className={styles.mapImage}/>
              )}
            </div>
         ))}
        </div>
    </div>
  )
}

export default MapGallery