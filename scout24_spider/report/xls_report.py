import xlsxwriter


class MakeReport:

    def __init__(self, **kwargs):
        self.dict = kwargs
        self.name = kwargs.get('name', 'report.xlsx')
        self.workbook = xlsxwriter.Workbook(self.name)

    def create_report(self):
        worksheet = self.workbook.add_worksheet()
        i = 1

        for key, value in self.dict.items():
            if str(key) is not 'name':
                key = str(key).capitalize().replace('_', ' ') + ':'

                worksheet.write('A' + str(i), key)
                worksheet.write('B' + str(i), value)
                i += 1

        self.workbook.close()


if __name__ == '__main__':
    report = MakeReport(name='homegate_dead_links_report.xlsx', dead_links_found='150', running_time_was='22:31')
    report.create_report()