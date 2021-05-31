/* eslint-disable @typescript-eslint/no-unused-vars */
import React, { useEffect, useState } from "react";
import {ThemeProvider, createMuiTheme} from "@material-ui/core/styles"
import Nav, { NavItem } from "components/Nav/Nav";
import styles from "./Layout.module.scss";
import logo_scout from "assets/logo_scout.png";
import Footer from "components/Footer/Footer";
import { Paper } from "@material-ui/core";


const header_scout = {
  icon: logo_scout,
  title: "Scout",
};

/* Scout Navigation items */
const scoutNavItems: Array<NavItem> = [
  { linkTitle: "Home", public: false, link: "/home" },
  { linkTitle: "Genes", public: false, link: "/genes" },
  { linkTitle: "Gene Panels", public: false, link: "/gene-panels" },
  { linkTitle: "Phenotype", public: false, link: "/phenotype" },
  { linkTitle: "Diagnoses", public: false, link: "/diagnoses" },
  { linkTitle: "Manages variants", public: false, link: "/manages-variants" },
  { linkTitle: "Users", public: false, link: "/users" },
  { linkTitle: "Institutes", public: false, link: "/institutes" },
  { linkTitle: "Dashboard", public: false, link: "/dashboard" },
  { linkTitle: "User guide", public: true, externalLink: "https://clinical-genomics.github.io/scout/" },
  { linkTitle: "Open issues", public: true, externalLink: "https://github.com/Clinical-Genomics/scout/issues" },
];

const Layout: React.FC = ({children}) => {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    /** Check local storage */
    const darkModeStorage = localStorage.getItem("darkMode");
    if (darkModeStorage !== undefined) {
      setDarkMode(darkModeStorage === "true");
      return;
    }

    // Check OS dark/light mode
    if (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      // Dark
      setDarkMode(true);
    }
  }, []);

  // TODO: Check if there is a better way to solve the asynchronous problem
  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    localStorage.setItem("darkMode", newMode.toString());
  };
const theme = createMuiTheme({
  palette: {
    type: darkMode ? "dark" : "light",
  }
});
  return (
    <ThemeProvider theme={theme}>
      <Paper>
      <div className={`${styles.Layout} ${darkMode ? "dark_mode" : ""}`}>
        <header>
          <Nav
            header={header_scout}
            navItems={scoutNavItems}
            darkMode={darkMode}
            toggleDarkMode={toggleDarkMode}
          />
        </header>
        <main>{children}</main>
        <Footer />
      </div>
      </Paper>
    </ThemeProvider>
  );
};

export default Layout;
