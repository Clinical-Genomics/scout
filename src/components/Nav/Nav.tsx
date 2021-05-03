import React from "react";
import { Link } from "react-router-dom";
import styles from "./Nav.module.scss";

export interface Header {
  icon?: string; // Path to icon
  title?: string; // Name of webpage
}

export interface NavItem {
  linkTitle: string;
  link?: string;
  dropdownList?: Array<NavItem>;
}

interface Props {
  header?: Header;
  navLinks: Array<NavItem>;
}

const Nav: React.FC<Props> = ({ header, navLinks }) => {
  /* const onClickNavItem = () => {
    console.log("test");
  }; */

  return (
    <nav className={styles.Nav}>
      <ul>
        {/* Header */}
        {header?.icon && header?.title && (
          <li>
            <Link to="/" className={styles.header} >
              {header?.icon && <img src={header.icon} alt="Logo" />}
              {header?.title && <span>{header.title}</span>}
            </Link>
          </li>
        )}

        {/* Nav items */}
        {navLinks.map((navItem) => (
          <li key={navItem.linkTitle}>
            {/* Link */}
            {navItem.link && <Link to={navItem.link}>{navItem.linkTitle}</Link>}

            {/* Dropdown */}
            {navItem.dropdownList && (
              <button className={"no-button-style"}>
                {navItem.linkTitle}
                {"v"}
              </button>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Nav;
