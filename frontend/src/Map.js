import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, FeatureGroup } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import axios from 'axios';
import './PopupStyles.css';
import Loader from './Loader';

const Home = ({ userEmail }) => {
  const [drawnItems, setDrawnItems] = useState(null);
  const [popupVisible, setPopupVisible] = useState(false);
  const [selectedOption, setSelectedOption] = useState('construcciones_sam');
  const [geoprocessStatus, setGeoprocessStatus] = useState('');
  const [checkInterval, setCheckInterval] = useState(null);
  const [processing, setProcessing] = useState(false);


  const handleCreated = (e) => {
    const { layer } = e;
    setDrawnItems(layer);
  };

  const handleSendClick = () => {
    if (drawnItems) {
      setPopupVisible(true);
    }
  };

  const handlePopupClose = () => {
    setPopupVisible(false);
  };

  const handleExecute = () => {
    console.log('Ejecutando el geoproceso:', selectedOption);
    setPopupVisible(false);
    setProcessing(true);

    if (drawnItems) {
      const bbox = drawnItems.getBounds();
      const bboxData = {
        xmin: bbox.getSouthWest().lng,
        ymin: bbox.getSouthWest().lat,
        xmax: bbox.getNorthEast().lng,
        ymax: bbox.getNorthEast().lat
      };

      const data = {
        bbox: bboxData,
        option: selectedOption,
        email: userEmail
      };

      axios.defaults.xsrfCookieName = 'csrftoken';
      axios.defaults.xsrfHeaderName = 'X-CSRFToken';
      axios.defaults.withCredentials = true;

      axios.post('http://127.0.0.1:8000/geoprocess/process', data)
        .then(response => {
          console.log('Respuesta de la API:', response.data);
          const geoprocessId = response.data.id; // Obtener el ID del geoproceso
          setGeoprocessStatus(geoprocessId);
          const intervalId = setInterval(() => checkGeoprocessStatus(geoprocessId), 5000);
          setCheckInterval(intervalId);
        })
        .catch(error => {
          console.error('Error al hacer la solicitud a la API:', error);
        });
    }
  };

  const checkGeoprocessStatus = (geoprocessId) => {
    axios.get(`http://127.0.0.1:8000/geoprocess/geoprocess-status/${geoprocessId}`)
      .then(response => {
        console.log('Estado del geoproceso:', response.data);
        if (response.data.status === 'Finalizado' || response.data.elapsed_time >= 180) {
          clearInterval(checkInterval);
          setCheckInterval(null);
          setPopupVisible(false);
        }
      })
      .catch(error => {
        console.error('Error al obtener el estado del geoproceso:', error);
      });
  };

  useEffect(() => {
    return () => {
      // Limpia el intervalo cuando el componente se desmonta
      if (checkInterval) {
        clearInterval(checkInterval);
        setProcessing(false); 
      }
    };
  }, [checkInterval]);


  return (
    <div style={{ position: 'relative', width: '100vw', height: 'calc(100vh - 60px)', overflow: 'hidden' }}>
      <MapContainer
        center={[-34.61, -58.38]}
        zoom={13}
        maxZoom={18}
        style={{ width: '100%', height: 'calc(100vh - 60px)', zIndex: 0, position: 'absolute' }}
      >
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
          // url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
          attribution="Tiles &copy; Esri"
        />

        <FeatureGroup>
          <EditControl
            position="topright"
            onCreated={handleCreated}
            draw={{
              rectangle: true,
              circle: false,
              circlemarker: false,
              marker: false,
              polyline: false,
              polygon: false
            }}
          />
        </FeatureGroup>
        
        {!popupVisible && drawnItems && (
          <button
            onClick={handleSendClick}
            style={{ position: 'absolute', bottom: '60px', left: '50%', transform: 'translateX(-50%)', zIndex: 1001, padding: '10px 20px', backgroundColor: '#007BFF', color: 'white', borderRadius: '4px', border: 'none', cursor: 'pointer',  fontSize: '16px' }}
          >
            Procesar
          </button>
        )}
      </MapContainer>

      {popupVisible && (
        <div className="popup" style={{ position: 'absolute', bottom: '40px', left: '50%', transform: 'translateX(-50%)', zIndex: 1002, padding: '20px', backgroundColor: 'white', boxShadow: '0px 0px 10px rgba(0, 0, 0, 0.2)', borderRadius: '8px' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '20px' }}>Selecciona un geoproceso</h3>
          
          <div style={{ marginBottom: '20px' }}>
            <h4>Detección y Segmentación</h4>
            <label>
              <input
                type="radio"
                value="construcciones"
                checked={selectedOption === 'construcciones_sam'}
                onChange={() => setSelectedOption('construcciones_sam')}
              />
              Construcciones
            </label>
            <label>
              <input
                type="radio"
                value="arboles"
                checked={selectedOption === 'arboles'}
                onChange={() => setSelectedOption('arboles')}
              />
              Árboles
            </label>
            <label>
              <input
                type="radio"
                value="piletas"
                checked={selectedOption === 'piletas'}
                onChange={() => setSelectedOption('piletas')}
              />
              Piletas
            </label>
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <h4>Índices de Clasificación</h4>
            <label>
              <input
                type="radio"
                value="agua"
                checked={selectedOption === 'agua'}
                onChange={() => setSelectedOption('agua')}
                disabled
              />
              Agua (en desarrollo)
            </label>
            <label>
              <input
                type="radio"
                value="vegetacion"
                checked={selectedOption === 'vegetacion'}
                onChange={() => setSelectedOption('vegetacion')}
                disabled
              />
              Vegetación (en desarrollo)
            </label>
            <label>
              <input
                type="radio"
                value="construcciones"
                checked={selectedOption === 'construcciones'}
                onChange={() => setSelectedOption('construcciones')}
                disabled
              />
              Construcciones (en desarrollo)
            </label>
          </div>
          
          <div className="button-container" style={{ textAlign: 'center' }}>
            <button onClick={handleExecute} style={{ backgroundColor: '#28A745', color: 'white', padding: '8px 16px', fontSize: '14px', borderRadius: '4px', border: 'none', cursor: 'pointer', marginRight: '10px' }}>
              Ejecutar
            </button>
            <button onClick={handlePopupClose} style={{ backgroundColor: '#007BFF', color: 'white', padding: '8px 16px', fontSize: '14px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>
              Cerrar
            </button>
          </div>
        </div>
      )}
      {processing && (
        <div
          style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            backgroundColor: 'rgba(0, 0, 0, 0.8)', // Cambiar color de fondo
            color: 'white', // Cambiar color del texto
            padding: '20px',
            borderRadius: '8px',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center'
          }}
        >
          <Loader /> 
        </div>
      )}
    </div>
  );
};

export default Home;
