<!DOCTYPE html>
<html lang="en" class="no-js">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LigoCAM @ LHO | ISI main</title>
        <link rel="stylesheet" type="text/css" href="css/style.css" />
    </head>
    
    <body>
        <div class="header" style="color:white; background-color:#7FA009;">
                  <h1>LigoCAM @ LHO | ISI </h1>
        </div>

        <div class="boxedmid">
            <form action="https://ldas-jobs.ligo.caltech.edu/~philippe.nguyen/test/ligocam_test/LigoCAM/ISI/LigoCamHTML_current.html" target="_blank">
                <p style="text-align: center;"><input type="submit" value="Latest page" style="width:60%; height:40px; color:#87099D; background-color:#D9BDDF; font-size:20px; margin-top:0px;"/></p>
            </form>
        </div> 
        
        <div class="container">
            <?php
                // Add years and hide specific months by modifying these arrays
                $months = array(1 => "Jan", 2 => "Feb", 3 => "Mar", 4 => "Apr", 5 => "May", 6 => "Jun", 7 => "Jul", 8 => "Aug", 9 => "Sep", 10 => "Oct", 11 => "Nov", 12 => "Dec");
                $years = array(2014, 2015, 2016, 2017, 2018, 2019);
                // Hide these months because LigoCAM was not running.
                $hide = array("01_2014", "02_2014", "03_2014", "12_2017",
                              "01_2018", "02_2018", "03_2018", "04_2018", "05_2018", "06_2018",
                              // "07_2018", "08_2018", "09_2018", "10_2018", "11_2018", "12_2018",
                              "01_2019", "02_2019", "03_2019", "04_2019", "05_2019", "06_2019", "07_2019", "08_2019", "09_2019", "10_2019", "11_2019", "12_2019");
                // Choose a font color and background color for each year/column
                $colors = array(
                    2014 => "0A67A1",
                    2015 => "FF9900",
                    2016 => "298000",
                    2017 => "7D3C98",
                    2018 => "0A67A1",
                    2019 => "FF9900"
                );
                $bgcolors = array(
                    2014 => "D8DCDE",
                    2015 => "FFFFCC",
                    2016 => "caffb3",
                    2017 => "E8DAEF",
                    2018 => "D8DCDE",
                    2019 => "FFFFCC"
                );
                foreach($years as $year) {
                    echo "<div class=\"boxedcalendarcenter\">\n";
                    foreach($months as $num => $month) {
                        $num_padded = sprintf("%02d", $num);
                        $datestring = $num_padded . "_" . $year;   // Formats the date to look like e.g. 01_2014 for Jan 2014
                        if (in_array($datestring, $hide)) {
                            // Hidden months are rendered as un-linked, un-labeled buttons
                            $url = "";
                            $bgcolor = $bgcolors[$year];
                            echo "\t\t\t\t";
                            echo "<form>\n";
                            echo "\t\t\t\t\t";
                            echo "<p style=\"text-align: center;\"><input type=\"submit\" value=\" \" ";  // No label assigned to "value" attribute
                            echo "style=\"width:100%; height:40px; background-color:#" . $bgcolor . "; font-size:20px; margin-top:0px;\"/>\n";
                            echo "\t\t\t\t";
                            echo "</form>\n";
                        } else {
                            // Visible months have link to results page and are labeled by month and year
                            $url = "https://ldas-jobs.ligo.caltech.edu/~philippe.nguyen/test/ligocam_test/LigoCAM/ISI/calendar/LigoCAM_" . $datestring . ".html";
                            $color = $colors[$year];
                            $bgcolor = $bgcolors[$year];
                            echo "\t\t\t\t";
                            echo "<form action=\"" . $url . "\" target=\"_blank\">\n";
                            echo "\t\t\t\t\t";
                            echo "<p style=\"text-align: center;\"><input type=\"submit\" value=\"" . $month . " " . $year . "\" ";
                            echo "style=\"width:100%; height:40px; color:#" . $color . "; background-color:#" . $bgcolor . "; font-size:20px; margin-top:0px;\"/>\n";
                            echo "\t\t\t\t";
                            echo "</form>\n";
                        }
                    }
                    echo "\t\t\t</div>\n\t\t\t";
                }
            ?>
        </div>
        <br>
        <div id="footer" style="background-color:white; float:bottom;">
            <table width="100%" height="3%"><tbody><tr><td align="right">Contact: dipongkar.talukder@ligo.org &nbsp;</td></tr></tbody></table>
        </div>
    </body>
</html>
