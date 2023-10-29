import './App.css';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Container from 'react-bootstrap/Container';
import Navbar from 'react-bootstrap/Navbar';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Map from './Map';
import ReportList from './ReportList';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.withCredentials = true;

const client = axios.create({
  baseURL: "http://127.0.0.1:8000"
});

function App() {
  const [currentUser, setCurrentUser] = useState();
  const [registrationToggle, setRegistrationToggle] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [loginError, setLoginError] = useState('');

  useEffect(() => {
    const userStatus = localStorage.getItem('currentUser');
    const storedEmail = localStorage.getItem('userEmail');
    if (userStatus === 'true') {
      setCurrentUser(true);
      setUserEmail(storedEmail);
    } else {
      setCurrentUser(false);
      setUserEmail('');
    }
  }, []);

  function update_form_btn() {
    if (registrationToggle) {
      document.getElementById("form_btn").innerHTML = "Registrarse";
      setRegistrationToggle(false);
    } else {
      document.getElementById("form_btn").innerHTML = "Iniciar Sesión";
      setRegistrationToggle(true);
    }
    setEmail('');
    setUsername('');
    setPassword('');
  }

  function submitRegistration(e) {
    e.preventDefault();
    client.post(
      "/api/register",
      {
        email: email,
        username: username,
        password: password
      }
    ).then(function(res) {
      client.post(
        "/api/login",
        {
          email: email,
          password: password
        }
      ).then(function(res) {
        localStorage.setItem('currentUser', 'true');
        setCurrentUser(true);
        setUserEmail(email);
        setEmail('');
        setUsername('');
        setPassword('');
      });
    });
    setEmail(''); // Limpiar campo de correo después de enviar
    setPassword(''); // Limpiar campo de contraseña después de enviar
  }

  function submitLogin(e) {
    e.preventDefault();
    client.post(
      "/api/login",
      {
        email: email,
        password: password
      }
    ).then(function(res) {
      localStorage.setItem('currentUser', 'true');
      localStorage.setItem('userEmail', email);
      setCurrentUser(true);
      setUserEmail(email);
      setEmail('');
      setPassword('');
      setLoginError('');
    }).catch(function(error) {
      if (error.response && error.response.status === 400) {
        setLoginError('Credenciales no válidas');
      }
    });
    setEmail(''); // Limpiar campo de correo después de enviar
    setPassword(''); // Limpiar campo de contraseña después de enviar
  }

  function submitLogout(e) {
    e.preventDefault();
    client.post(
      "/api/logout",
      {withCredentials: true}
    ).then(function(res) {
      localStorage.removeItem('currentUser');
      localStorage.removeItem('userEmail');
      setCurrentUser(false);
      setUserEmail('');
      window.location.href = '/';
    });
  }

  return (
    <div className="app-container">
      <Router>
        <Navbar bg="dark" variant="dark">
          <Container>
            <Navbar.Brand>
            <Link to="/" className="nav-link btn btn-light me-2" onClick={() => { if(window.location.pathname === "/") window.location.reload() }}>
                Plataforma Terradata
              </Link>
            </Navbar.Brand>
            <Navbar.Toggle />
            <Navbar.Collapse className="justify-content-end">
              <Navbar.Text>
                <div className="d-flex align-items-center">
                  {currentUser && (
                    <div className="d-flex align-items-center">
                      <span className="me-2">Hola {userEmail}</span>
                      <Link to="/reports" className="nav-link btn btn-light me-2">
                        Ver Reportes
                      </Link>
                      <form onSubmit={e => submitLogout(e)}>   
                        <Button type="submit" variant="light">Cerrar Sesión</Button>
                      </form>
                    </div>
                  )}
                  {!currentUser && (
                    <Button id="form_btn" onClick={update_form_btn} variant="light">
                      Registrarse
                    </Button>
                  )}
                </div>
              </Navbar.Text>
            </Navbar.Collapse>
          </Container>
        </Navbar>

        <Routes>
          {currentUser ? (
            <>
              <Route path="/" element={<Map userEmail={userEmail} />} />
              <Route path="/reports" element={<ReportList userEmail={userEmail} />} />
            </>
          ) : (
            <>
              {/* Renderizar Mapa para usuarios no autenticados si es necesario */}
              {/* Agregar más rutas aquí si es necesario */}
            </>
          )}
        </Routes>

        {!currentUser && registrationToggle && ( 
          <div className="center">
            <Form onSubmit={e => submitRegistration(e)}>
              <Form.Group className="mb-3" controlId="formBasicEmail">
                <Form.Label>Correo Electrónico</Form.Label>
                <Form.Control type="email" placeholder="Ingrese su email" value={email} onChange={e => setEmail(e.target.value)} required />
                <Form.Text className="text-muted">
                  Nunca compartiremos su correo electrónico con nadie más.
                </Form.Text>
              </Form.Group>
              <Form.Group className="mb-3" controlId="formBasicUsername">
                <Form.Label>Usuario</Form.Label>
                <Form.Control type="text" placeholder="Ingrese su usuario" value={username} onChange={e => setUsername(e.target.value)} required />
              </Form.Group>
              <Form.Group className="mb-3" controlId="formBasicPassword">
                <Form.Label>Contraseña</Form.Label>
                <Form.Control type="password" placeholder="Ingrese su contraseña" value={password} onChange={e => setPassword(e.target.value)} required />
              </Form.Group>
              <Button variant="primary" type="submit">
                Registrarse
              </Button>
            </Form>
          </div>        
        ) } 

        {!currentUser && !registrationToggle && (
          <div className="center">
            <div className="d-flex justify-content-between">
              <Form onSubmit={e => submitLogin(e)}>
                <Form.Group className="mb-3" controlId="formBasicEmail">
                  <Form.Label>Correo Electrónico</Form.Label>
                  <Form.Control type="email" placeholder="Ingrese su email" value={email} onChange={e => setEmail(e.target.value)} required />
                  <Form.Text className="text-muted">
                    Nunca compartiremos su correo electrónico con nadie más.
                  </Form.Text>
                </Form.Group>
                <Form.Group className="mb-3" controlId="formBasicPassword">
                  <Form.Label>Contraseña</Form.Label>
                  <Form.Control type="password" placeholder="Ingrese su contraseña" value={password} onChange={e => setPassword(e.target.value)} required />
                </Form.Group>
                <Button variant="primary" type="submit">
                  Iniciar Sesión
                </Button>
                {loginError && <div className="text-danger">{loginError}</div>}
              </Form>
            </div>
          </div>
        )}

        {!currentUser && (
          <footer className="footer">
            <div className="text-center text-white">
              <p>Terradata &copy; 2023</p>
            </div>
          </footer>
        )}
      </Router>
      
    </div>
  );
}

export default App;
