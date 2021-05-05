import React from "react";
import styles from "./DropdownMenu.module.scss";

const DropdownMenu: React.FC = ({ children }) => (
  <ul className={styles.DropdownMenu}>{children}</ul>
);
export default DropdownMenu;
