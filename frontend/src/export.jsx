import React from 'react';
import { Document, Page, Text, View, StyleSheet, PDFDownloadLink } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  page: {
    flexDirection: 'column',
    backgroundColor: '#FFFFFF',
    padding: 30
  },
  title: {
    fontSize: 24,
    marginBottom: 20,
    textAlign: 'center'
  },
  table: {
    display: 'table',
    width: '100%',
    borderStyle: 'solid',
    borderWidth: 1,
    borderColor: '#000',
    marginBottom: 10
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#000',
    minHeight: 30,
    alignItems: 'center'
  },
  tableHeader: {
    backgroundColor: '#E4E4E4'
  },
  tableCol: {
    width: '33%',
    padding: 5
  },
  tableCell: {
    fontSize: 10,
    padding: 5
  }
});

const TokensPDF = ({ tokens }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      <Text style={styles.title}>SOOP Lexical Analysis</Text>
      <View style={styles.table}>
        <View style={[styles.tableRow, styles.tableHeader]}>
          <View style={styles.tableCol}>
            <Text style={styles.tableCell}>Value</Text>
          </View>
          <View style={styles.tableCol}>
            <Text style={styles.tableCell}>Type</Text>
          </View>
          <View style={styles.tableCol}>
            <Text style={styles.tableCell}>Line</Text>
          </View>
        </View>
        {tokens.map((token, index) => (
          <View key={index} style={styles.tableRow}>
            <View style={styles.tableCol}>
              <Text style={styles.tableCell}>{token.value}</Text>
            </View>
            <View style={styles.tableCol}>
              <Text style={styles.tableCell}>{token.type}</Text>
            </View>
            <View style={styles.tableCol}>
              <Text style={styles.tableCell}>{token.line}</Text>
            </View>
          </View>
        ))}
      </View>
    </Page>
  </Document>
);

const ExportPDFButton = ({ tokens }) => (
  <PDFDownloadLink
    document={<TokensPDF tokens={tokens} />}
    fileName="lexical-analysis.pdf"
    className="btn btn-secondary px-4 py-2 ms-2"
  >
    {({ loading }) => (loading ? 'Generating PDF...' : 'Export to PDF')}
  </PDFDownloadLink>
);

export default ExportPDFButton;