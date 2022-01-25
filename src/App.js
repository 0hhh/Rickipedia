import React, { useState,useEffect } from 'react';
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.min.js";
import Cards from "./components/Cards/Cards";
import Filter from "./components/Filters/Filter"
import Pagination from './components/Pagination/Pagination';

function App() {

  let [pageNumber, setPageNumber] = useState(1);
  let [fetchedData, upadateFetchedData] = useState([]);
  let { info, results} = fetchedData;

  let api = `https://rickandmortyapi.com/api/character/?page=${pageNumber}` ;
  
  useEffect(()=>{
    // function abc(){}
    // let abcd = ()=>{}
    (async function(){
      let data =  await fetch(api).then(res=>res.json());
      upadateFetchedData(data);
    })()
  },[api])

  return (
    <div className="App">
      <h1 className="text-center ubuntu my-4">
        <span className="text-info">Rick</span>ipedia
      </h1>

      <div className="container">
        <div className="row">
          <div className="col-3">
            <Filter/>
          </div>
          <div className="col-8">
            <div className="row">
              <Cards results={results}/>
            </div>
          </div>
        </div>
      </div>

      <Pagination setPageNumber={setPageNumber}/>
    </div>
  ); 
}

export default App;
