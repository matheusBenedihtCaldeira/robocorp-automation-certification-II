from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    close_annoying_modal()
    get_orders()
    fill_the_form()
    archive_receipts()


def open_robot_order_website():
    """Open the robot order website"""
    browser.goto('https://robotsparebinindustries.com/#/robot-order')

def close_annoying_modal():
    """Close the popup window"""
    page = browser.page()
    page.click('button:text("Ok")')

def get_orders():
    """Get the orders data in .csv file"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv('orders.csv', header=True)
    return orders

def fill_the_form():
    """Fill the order form"""
    orders = get_orders()
    for row in orders:
        page = browser.page()
        page.select_option('#head', row["Head"])
        page.click(f'//*[@id="id-body-{row["Body"]}"]')
        page.fill('input[placeholder="Enter the part number for the legs"]', row["Legs"])
        page.fill('#address', row['Address'])
        page.click('//button[@id="order"]')
        while not page.query_selector('//button[@id="order-another"]'):
            page.click('//button[@id="order"]')
        pdf_path = store_receipt_as_pdf(int(row['Order number']))
        screenshot_path = screenshot_robot(int(row['Order number']))
        embed_screenshot_to_receipt(screenshot_path, pdf_path)
        page.click('//button[@id="order-another"]')
        close_annoying_modal()    

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt = page.locator('#receipt').inner_html()
    pdf = PDF()
    pdf_path = 'output/receipts/{0}.pdf'.format(order_number)
    pdf.html_to_pdf(receipt, pdf_path)
    return pdf_path

def screenshot_robot(order_number):
    page = browser.page()
    screenshot_path = "output/screenshots/{0}.png".format(order_number)
    page.locator('#robot-preview-image').screenshot(path=screenshot_path)
    return screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(image_path=screenshot, 
                                   source_path=pdf_file, 
                                   output_path=pdf_file)
    
def archive_receipts():
    archive = Archive()
    archive.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")