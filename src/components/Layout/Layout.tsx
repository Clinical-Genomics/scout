/* eslint-disable @typescript-eslint/no-unused-vars */
import React, { useEffect, useState } from "react";
import Nav, { NavItem } from "components/Nav/Nav";
import styles from "./Layout.module.scss";
import logo_scout from "assets/logo_scout.png";
import logo_cg from "assets/logo_cg.svg";
import Footer from "components/Footer/Footer";

const header_cg = {
  icon: logo_cg,
  title: "Clinical Genomics",
};
const header_scout = {
  icon: logo_scout,
  title: "Scout",
};

const cgNavItems: Array<NavItem> = [
  { linkTitle: "Beställninger", public: true, link: "/orders" },
  { linkTitle: "Provkrav", public: true, link: "/requirements" },
  { linkTitle: "Applikationer", public: true, link: "/applications" },
  { linkTitle: "Dataleverans", public: true, link: "/delivery" },
  {
    linkTitle: "Support",
    public: true,
    dropdownList: [
      { linkTitle: "FAQ", public: true, link: "/faq" },
      { linkTitle: "Kontakt", public: true, link: "/contact" },
      { linkTitle: "Feedback", public: false, link: "/feedback" },
      { linkTitle: "Help", public: false, link: "/help" },
    ],
  },
  { linkTitle: "New order", public: false, link: "/new-order" },
  { linkTitle: "Status", public: false, link: "/status" },
  { linkTitle: "Items", public: false, link: "/items" },
];

const Layout: React.FC = ({ children }) => {
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

  return (
    <div className={`${styles.Layout} ${darkMode ? "dark_mode" : ""}`}>
      <header>
        <Nav
          header={header_cg}
          navItems={cgNavItems}
          darkMode={darkMode}
          toggleDarkMode={toggleDarkMode}
        />
      </header>
      <main>{children}</main>
      <Footer />
    </div>
  );
};

export default Layout;
