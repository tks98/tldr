import React, { useState } from "react";
import styled from "styled-components";
import { ClipLoader } from "react-spinners";

function App() {
  return PdfUploader();
}

export default App;

export const PdfUploader = () => {
  const [pdf, setPdf] = useState(null);
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (event) => {
    setPdf(event.target.files[0]);
  };

  const handleSubmit = async () => {
    // show the spinner when the submission starts
    setIsLoading(true);

    try {
      const data = new FormData();
      data.append("pdf", pdf);

      const response = await fetch("http://localhost:5001/summarize", {
        method: "POST",
        body: data,
      });

      const responseText = await response.text();
      // stop the spinner and set the response
      setIsLoading(false);
      setResponse(responseText);
    } catch (error) {
      console.error(error);
    }
  };

  const StyledInput = styled.input`
    width: 400px;
    font-size: 20px;
    display: none;
  `;

  const StyledLabel = styled.label`
    font-size: 20px;
    cursor: pointer;
    display: inline-block;
    padding: 0.75em 1.5em;
    color: #fff;
    background: #000;
    text-decoration: none;
    border: 0;
    border-radius: 4px;
    transition: background 0.3s ease;

    &:hover {
      background: #333;
    }

    &:active {
      background: #777;
    }
  `;

  const StyledButton = styled.button`
    font-size: 20px;
  `;

  const StyledTextarea = styled.textarea`
    font-size: 20px;
    width: 400px;
  `;

  const StyledAnchor = styled.a`
    margin-top: 1em;
    display: inline-block;
  `;

  return (
    <div
      style={{
        background: "#eee",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <h1>tl;dr</h1>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          marginBottom: "1em",
        }}
      >
        {/* Use a styled <label> element and a hidden <input> element to create a custom "Choose file" button that allows the user to select a PDF file */}
        <StyledLabel htmlFor="pdf-input">Choose file</StyledLabel>
        <StyledInput
          type="file"
          accept="application/pdf"
          id="pdf-input"
          onChange={handleChange}
        />
        {/* Show the selected file name only if a PDF file has been selected */}
        {pdf && <p>File selected: {pdf.name}</p>}
      </div>
      <StyledButton onClick={handleSubmit}>Submit</StyledButton>
      {/* Add text that says "Summary" above the result box */}
      {response && (
        <>
          <h2>Summary</h2>
          <StyledTextarea value={response} readOnly rows={10} cols={50} />
        </>
      )}
      {/* Add the ClipLoader component to show while the response is being awaited */}
      {isLoading && (
        <div
          style={{
            marginTop: "1em",
            display: "flex",
            justifyContent: "center",
          }}
        >
          <ClipLoader />
        </div>
      )}
      {/* Add a GitHub logo that takes the user to a website when clicked */}
      <StyledAnchor href="https://github.com/tks98" target="_blank">
        <img src="https://github.com/favicon.ico" alt="GitHub logo" />
      </StyledAnchor>
    </div>
  );
};
