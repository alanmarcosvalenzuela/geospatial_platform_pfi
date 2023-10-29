import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Table from 'react-bootstrap/Table';
import Container from 'react-bootstrap/Container';
import ReactPaginate from 'react-paginate';
import './ReportList.css'; // Importa el archivo CSS

const ReportList = ({ userEmail }) => {
  const [reports, setReports] = useState([]);
  const [currentPage, setCurrentPage] = useState(0);
  const perPage = 15;

  const handlePageClick = (data) => {
    setCurrentPage(data.selected);
  };

  useEffect(() => {
    axios
      .get(`http://127.0.0.1:8000/geoprocess/reports/${userEmail}/`)
      .then((response) => {
        setReports(response.data.user_reports);
      })
      .catch((error) => {
        console.error('Error fetching reports:', error);
      });
  }, [userEmail, currentPage]);

  const offset = currentPage * perPage;
  const currentPageData = reports.slice(offset, offset + perPage);

  return (
    <div>
      <Container>
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>ID</th>
              <th>Título</th>
              <th>Descripción</th>
              <th>Status</th>
              <th>Archivo</th>
            </tr>
          </thead>
          <tbody>
            {currentPageData.map((report) => (
              <tr key={report.id}>
                <td>{report.id}</td>
                <td>{report.title}</td>
                <td>{report.description}</td>
                <td>{report.status}</td>
                <td>
                  <a href={report.file} target="_blank" rel="noopener noreferrer">
                    Descargar
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Container>

      <Container className="pagination-container">
        <ReactPaginate
          previousLabel={currentPage !== 0 ? 'Anterior' : null}
          nextLabel={currentPage !== Math.ceil(reports.length / perPage) - 1 ? 'Siguiente' : null}
          breakLabel={'...'}
          pageCount={Math.ceil(reports.length / perPage)}
          marginPagesDisplayed={2}
          pageRangeDisplayed={5}
          onPageChange={handlePageClick}
          containerClassName={'pagination'}
          subContainerClassName={'pages pagination'}
          activeClassName={'active'}
          disableInitialCallback={true}
        />
      </Container>
    </div>
  );
};

export default ReportList;
