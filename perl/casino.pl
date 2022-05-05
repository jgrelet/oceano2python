#!/usr/bin/perl -w
#
# casino.pl   J Grelet IRD juillet 2012 - mars 2016
# $Id$
# analyse fichiers casino Genavir
# usage ./casino.pl 
#

use strict;

use Time::Local;
use Date::Manip;
use File::Basename;
use Getopt::Long;
use Oceano::Convert;

#------------------------------------------------------------------------------
# Les repertoires de sorties
#------------------------------------------------------------------------------
my $ascii_dir = 'ascii/';
my $odv_dir   = 'odv/';

#------------------------------------------------------------------------------
# Les variables globales
#------------------------------------------------------------------------------
our $VERSION       = '1.1';
our $AUTHOR        = 'J Grelet - P Rousselot - PIRATA-FR29 - march 2019';
my  $DEBUG         = 0;
my  $ECHO;

# noms de fichiers
my $cruise         = "PIRATA-FR29";
my $path_cruise_name = lc $ascii_dir.$cruise;
my $sst_hdr_file   = $path_cruise_name.'.tsg';
my $sst_file       = $path_cruise_name.'_tsg';
my $snd_hdr_file   = $path_cruise_name.'.snd';
my $snd_file       = $path_cruise_name.'_snd';
my $tsgqc_file     = $path_cruise_name.'.tsgqc';
my $mto_hdr_file   = $path_cruise_name.'.mto';
my $mto_file       = $path_cruise_name.'_mto';
my $fbox_file      = $path_cruise_name.'_fbox';
my $fbox_hdr_file  = $path_cruise_name.'.fbox';

# handle des fichiers
# handles de fichiers
my  $TSGQC_HDL     = undef;

my $ship           = "THALASSA";
my $institute      = "IRD";
my $mto_instrument = "BATOS";
my $sst_instrument = "SBE21";
my $fbox_instrument = "FERRYBOX";
my $snd_instrument = "EK80-TECHSAS";
my $sst_sn         = "N/A";
my $mto_sn         = "N/A";
my $snd_sn         = "N/A";
my $fbox_sn         = "N/A";

# surcharge par la valeurs saisies sur la ligne de commande
my  $version;
my  $software         = "CASINO";
my  $software_version = "V2.6.1";
my  $validation_comment = "Extraction réalisée sur fichier .csv de CASINO";
my  $pi            = "BOURLES";
my  $CONTEXTE      = "AMMA";
my  $TIMEZONE      = "GMT";
my  $FORMAT_DATE   = "DMY";
my  $CODE          = "1A";
my  $date_debut    = "01/03/2019";
my  $date_fin      = "04/04/2019";

my  $help;
my  $xml           = undef;       # par defaut, sortie XML activee
my  $ascii         = undef;   
my  $odv           = undef;   
my  $all           = undef;   
my  $dtd           = undef;

my ($j,$dif_met,$dif_sbe);
my ($jmet, $jsbe);
my ($cycle_mesure, $plateforme, $probe) = undef;
my ($julien, $lat_s,$lat_deg, $lat_min, $lat_sec, $lat_dec);
my ($long_s,$long_deg, $long_min, $long_sec, $long_dec);
my ($day,$month,$year,$hour,$min,$sec);
my ($time, $ecart);
my ($date,$heure,$code,$lat,$long,$sonde,$tair,$tmer,$hum,$patm,$rad,
    $vit,$dir,$CNDC,$SSTP,$SSPS,$SSJT);
# thalassa FR29
my ($phinsb,$phinst,$speed,$heading,$DOX2);
my ($sog, $cog,$speed_drift,$heading_drift);
# FerryBox
my ($fbox_QC,$SSPS_45,$TUR4,$Greenalgea,$BlueAlgae,$Diatoms,$Cryptophyta,$YellowSub,$CPHL,$PHPH);

#------------------------------------------------------------------------------
# version()
#------------------------------------------------------------------------------	
sub version() {
  print "Version: $VERSION\nAuthor: $AUTHOR\n\n";	
  exit 1;
}

#------------------------------------------------------------------------------
# usage()
#------------------------------------------------------------------------------	
sub usage() {
  print STDERR "\nusage: perl casino.pl [options]\n\n";
  print STDERR   "Options:\n    --help                 Display this help message\n";
  print STDERR   "    --version              program version\n";
  print STDERR   "    --debug=[1-3]          debug info\n";
  print STDERR   "    --echo                 display filenames processed\n";
  print STDERR   "    --cycle_mesure=<name>  give cruise name\n";
  print STDERR   "    --plateforme=<name>    ship or plateforme name\n";
  print STDERR   "    --date_debut=JJ/MM/YYYY   starting date from cycle_mesure\n";
  print STDERR   "    --date_fin  =JJ/MM/YYYY   end date from cycle_mesure\n";

  print STDERR   "    --institute=<name>     institute name\n";
  print STDERR   "    --code_oopc=<value>    processing code\n";
  print STDERR   "    --pi=<pi_name> \n";
  print STDERR   "    --local                use local DTD\n";
  print STDERR   "    --type=<instrument_type> \n";
  print STDERR   "    --sn=<instrument_serial_number> \n";
  print STDERR   "    --software=<software_name> \n";
  print STDERR   "    --software_version=<software_version> \n";
  print STDERR   "    --xml                  only XML output (default)\n";
  print STDERR   "    --ascii                only ASCII output\n";
  print STDERR   "    --odv                  only ODV output\n";
  print STDERR   "    --all                  ASCII,XML and ODV output\n";
  print STDERR   "\naccept short options like -d1 -t2\n\n";
  print STDERR   "CASINO example:\n------------\n\$ perl casino.pl --cycle_mesure=$cruise --institute=$institute --plateforme=$ship --pi=$pi --date_debut=$date_debut --date_fin=$date_fin --echo --local data/*.csv --all\n\n"; 
  exit 1;
}


#------------------------------------------------------------------------------
# get_options()
# analyse les options
#------------------------------------------------------------------------------	
sub get_options() {
  
  &GetOptions ("cycle_mesure=s"     => \$cycle_mesure,    
               "software=s"         => \$software,  
               "software_version=s" => \$software_version,  
               "plateforme=s"       => \$plateforme,  
               "date_debut=s"       => \$date_debut,  
               "date_fin=s"         => \$date_fin,  	       
               "pi=s"               => \$pi,
               "code_oopc=s"        => \$CODE,  
               "ascii"              => \$ascii,  
               "xml"                => \$xml,  
               "odv"                => \$odv,	 
               "all"                => \$all,	 
               "debug=i"            => \$DEBUG,  
               "echo"               => \$ECHO,  
               "institute=s"        => \$institute,  
               "local"              => \$dtd,  
               "version"            => \$version,  
               "help"               => \$help)  or &usage;  
       
  &version if $version;	
  &usage   if $help;	

  # xml by default
  $xml = 1 if (!defined $ascii && !defined $odv); 
  if ($all) { $ascii = $odv = $xml = 1; }
}

#------------------------------------------------------------------------------
# fonctions de calcul de la position/date
#------------------------------------------------------------------------------
sub position {
  my($deg,$min,$sec,$hemi)=@_;
  my $sign = 1;
  if( $hemi eq "S" || $hemi eq "W") {
    $sign = -1;
  }
  return( ( $deg + ( $min / 60 ) + ( $sec / 3600 ) ) * $sign ); 
}

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#sub julian {
#  my($jj,$h,$m,$s)=@_;
#  #print "$jj $h $m $s\n";
#  my $tmp = ( ($h * 3600) + ( $m * 60 ) +$s ) / (1440 * 60);
#  return( $jj + $tmp ); 
#}

#------------------------------------------------------------------------------
# entete TSGQC
#------------------------------------------------------------------------------
sub entete_tsgqc { 
  my($handle) = @_;

  print $handle "%PLATFORM_NAME $ship\n";
  print $handle "%HEADER YEAR MNTH DAYX hh mi ss LATX LONX SSPS SSPS_QC SSPS_ADJUSTED SSPS_ADJUSTED_ERROR SSPS_ADJUSTED_QC SSJT SSJT_QC SSJT_ADJUSTED SSJT_ADJUSTED_ERROR SSJT_ADJUSTED_QC SSTP SSTP_QC SSTP_ADJUSTED SSTP_ADJUSTED_ERROR SSTP_ADJUSTED_QC\n";
}

#------------------------------------------------------------------------------
# Debut du programme principal
#------------------------------------------------------------------------------
#&Date_Init( "TZ=UTC","Language=French","DateFormat=non-US" );
&Date_Init( 'SetDate=now,UTC',"Language=French","DateFormat=non-US");

&get_options;

mkdir($ascii_dir) unless(-d $ascii_dir);
open( SST_FILE,  "+> $sst_hdr_file" ) or die "Can't open file : $sst_hdr_file\n";
open( SSTD_FILE, "+> $sst_file" )     or die "Can't open file : $sst_file\n";
open( $TSGQC_HDL,"+> $tsgqc_file" )   or die "Can't open file : $tsgqc_file\n";
open( SND_FILE,  "+> $snd_hdr_file" ) or die "Can't open file : $snd_hdr_file\n";
open( SNDD_FILE, "+> $snd_file" )     or die "Can't open file : $snd_file\n";
open( MTO_FILE,  "+> $mto_hdr_file" ) or die "Can't open file : $mto_hdr_file\n";
open( MTOD_FILE, "+> $mto_file" )     or die "Can't open file : $mto_file\n";
open( FBOX_FILE,  "+> $fbox_hdr_file" ) or die "Can't open file : $fbox_hdr_file\n";
open( FBOXD_FILE, "+> $fbox_file" )   or die "Can't open file : $fbox_file\n";

print SST_FILE  "$cruise  $ship  $institute  $sst_instrument $sst_sn\n";
print SSTD_FILE "$cruise  $ship  $institute  $sst_instrument $sst_sn\n";
print SND_FILE  "$cruise  $ship  $institute  $snd_instrument $snd_sn\n";
print SNDD_FILE "$cruise  $ship  $institute  $snd_instrument $snd_sn\n";
print MTO_FILE  "$cruise  $ship  $institute  $mto_instrument $mto_sn\n";
print MTOD_FILE "$cruise  $ship  $institute  $mto_instrument $mto_sn\n";
print FBOX_FILE  "$cruise  $ship  $institute  $fbox_instrument $fbox_sn\n";
print FBOXD_FILE "$cruise  $ship  $institute  $fbox_instrument $fbox_sn\n";

print SST_FILE  "   Date     Time      Latitude     Longitude    SSJT    SSPS   CNDC   SSTP\n";
print SSTD_FILE "YEAR    DAYD      LATX      LONX    SSJT   SSPS   CNDC   SSTP\n";
print SND_FILE  "   Date     Time      Latitude     Longitude    BATH      SOG    COG  SPEED   HEADING  SPEED_DRIFT HEADING_DRIFT PHINSB   PHINST\n";
print SNDD_FILE "YEAR    DAYD      LATX      LONX   BATH      SOG    COG  SPEED   HEADING  SPEED_DRIFT HEADING_DRIFT PHINSB   PHINST\n";
print MTO_FILE  "   Date     Time      Latitude     Longitude    SSTP   DRYT  WMSP  WDIR".
                "  ATMS  RELH   RDIN\n"; 
print MTOD_FILE "YEAR    DAYD      LATX      LONX    SSTP  DRYT  WMSP  WDIR   ATMS  RELH    RDIN\n"; 
print FBOX_FILE  "   Date     Time      Latitude     Longitude    DOXY   SSPS   TUR4  Greenalgea BlueAlgae Diatoms  Cryptophyta YellowSu  CPHL   PHPH\n";
print FBOXD_FILE "YEAR    DAYD      LATX      LONX    DOXY   SSPS   TUR4  Greenalgea BlueAlgae Diatoms  Cryptophyta YellowSub CPHL   PHPH\n";

&entete_tsgqc($TSGQC_HDL);

$jmet = $jsbe = $dif_met = $dif_sbe = 0;

# pour la campagne, on traite les donnees tous les jours, donc le directive DATA
# n'est pas utilise, on utilise le nom des fichiers passes en argument
# 
# while( <DATA> ){
#   open( FILE, $_ );
#   print STDERR "Lit : $_";
for( my $i = 0; $i <= $#ARGV; $i++ ){
  my $path = $ARGV[$i];
  open( FILE, $path );
  my ($name,$dir) = fileparse $path;
  print STDERR "Lit : $dir$name\n";
LINE: 
  while( <FILE> ){           # header contient l'entete
    next LINE if $. == 1;    # saute la premiere ligne d'entete
    next LINE if $_ eq "\n";   # saute les lignes vides
    #print "Ligne: $_\n";
    ($date,$heure,$lat,$long,undef,undef,$code,undef,undef,undef,  #10
    undef,undef,undef,undef,undef,undef,undef,undef,undef,undef,   #20
    undef,undef,undef,undef,undef,undef,undef,undef,undef,undef,   #30
    undef,undef,undef,undef,undef,$sonde,undef,undef,undef,undef,   #40
    undef,undef,undef,undef,undef,undef,undef,undef,undef,undef,   #50
    undef,undef,undef,undef,undef,undef,undef,$tair,$tmer,$hum,    #60
    $patm,$rad,undef,undef,undef,$vit,$dir,undef,undef,undef,      #70
    undef,undef,undef,undef,undef,undef,undef,$phinsb,undef,undef, #80
    undef,undef,undef,$phinst,undef,undef,undef,undef,undef,undef, #90
    undef,undef,undef,undef,$SSTP,$SSJT,$CNDC,$SSPS,undef,undef,   #100
    undef,undef,undef,undef,undef,undef,$sog,$cog,$speed,$heading, #110
    $speed_drift,$heading_drift,undef,undef,undef,undef,undef,undef,undef,undef,   #120
    undef,undef,undef,undef,undef,undef,undef,$fbox_QC,undef,undef,   #130
    undef,$SSPS_45,undef,$DOX2,undef,undef,$TUR4,$Greenalgea,$BlueAlgae,$Diatoms,  #140
    $Cryptophyta,$YellowSub,undef,$CPHL,$PHPH)
         = split(/\t/);
    #next LINE if $mode !~ /GPS/;  # si pas GPS on saute la ligne
				    # car donnees a zero
    next LINE if $code !~ /ACQAUTO/;  # si pas GPS on saute la ligne
    #next LINE if $SSTP !~ /\d/;  # si pas valeur SSTP, saute, bug casino 
    #$sonde = $code = 0; #on aurait pu les sauter avec undef
    # remplace le separateur , par un .
    #$lat_dec =~ s/\,/\./mg; 
    #$long_dec =~ s/\,/\./mg; 
    $SSJT =~ s/\,/\./mg; 
    $SSTP =~ s/\,/\./mg; 
    $CNDC =~ s/\,/\./mg; 
    $SSPS =~ s/\,/\./mg; 
    $tmer =~ s/\,/\./mg; 
    $tair =~ s/\,/\./mg; 
    $patm =~ s/\,/\./mg; 
    $vit =~ s/\,/\./mg; 
    $dir =~ s/\,/\./mg; 
    $rad =~ s/\,/\./mg; 
    $hum =~ s/\,/\./mg; 
    #   $fluo =~ s/\,/\./mg; 
    $sonde =~ s/\,/\./mg; 
    $sog =~ s/\,/\./mg; 
    $cog =~ s/\,/\./mg; 
    $speed =~ s/\,/\./mg; 
    $heading =~ s/\,/\./mg; 
    $DOX2 =~ s/\,/\./mg; 
    $speed_drift =~ s/\,/\./mg;
    $heading_drift =~ s/\,/\./mg;
    $phinsb =~ s/\,/\./mg; 
    $phinst =~ s/\,/\./mg; 
    $SSPS_45 =~ s/\,/\./mg; 
    $TUR4 =~ s/\,/\./mg; 
    $Greenalgea =~ s/\,/\./mg; 
    $BlueAlgae =~ s/\,/\./mg; 
    $Cryptophyta =~ s/\,/\./mg; 
    $Diatoms =~ s/\,/\./mg; 
    $YellowSub =~ s/\,/\./mg; 
    $CPHL =~ s/\,/\./mg; 
    $PHPH =~ s/\,/\./mg; 

    # change bad value with 1e36
    $SSJT = 1e36 if $SSJT eq "" or $SSJT < 0;
    $SSPS = 1e36 if $SSPS eq "" or $SSPS < 0;
    $CNDC = 1e36 if $CNDC eq "" or $CNDC < 0;
    $SSTP = 1e36 if $SSTP eq "" or $SSTP < 0;
    ($CNDC = $SSJT = $SSPS = 1e36) if $CNDC eq "";
    $tmer = 1e36 if $tmer eq "" or $tmer < 0;
    $tair = 1e36 if $tair eq "" or $tair < 0;
    $patm = 1e36 if $patm eq "" or $patm < 0;
    $vit = 1e36  if $vit  eq "" or $vit < 0;
    $dir = 1e36 if $dir eq "" or $dir < 0;
    $rad = 0 if $rad eq "" or $rad < 0;
    #$rad = $rad * 10.0;   # conversion mW/cm2 en W/m2
    $hum = 1e36 if $hum eq ""  or $hum < 0;
    $sonde = 1e36 if $sonde  <= 0 ;
    $sog = 1e36 if $sog  < 0;
    $cog = 1e36 if $cog  < 0;
    $speed_drift = 1e36 if $speed_drift  < 0;
    $heading_drift = 1e36 if $heading_drift  < 0;
    $speed = 1e36 if $speed  < 0;
    $heading = 1e36 if $heading  < 0;
    $phinsb = 1e36 if $phinsb  < 0;
    $phinst = 1e36 if $phinst  < 0;
    $DOX2 = 1e36 if $DOX2  < 0 or $fbox_QC > 0;
    $SSPS_45 = 1e36 if $SSPS_45  < 0 or $fbox_QC > 0;
    $TUR4 = 1e36 if $TUR4 < 0 or $fbox_QC > 0;
    $Greenalgea = 1e36 if $Greenalgea < 0 or $fbox_QC > 0;
    $BlueAlgae = 1e36 if $BlueAlgae < 0 or $fbox_QC > 0;
    $Cryptophyta = 1e36 if $Cryptophyta < 0 or $fbox_QC > 0;
    $Diatoms = 1e36 if $Diatoms < 0 or $fbox_QC > 0;
    $YellowSub = 1e36 if $YellowSub < 0 or $fbox_QC > 0;
    $CPHL = 1e36 if $CPHL < 0 or $fbox_QC > 0;
    $PHPH = 1e36 if $PHPH < 0 or $fbox_QC > 0;
    
    #$fluo = 1e36 if $fluo eq "" or $fluo == -4096;
    #print $date . " " . $heure ."\n"; 
        
    # decodage de la date et heure 
    if( $date =~ m[(\d+)/(\d+)/(\d+)]) {
      ($day,$month,$year) = ($1, $2, $3);	
    }	
    if( $heure =~ /(\d+):(\d+):(\d+)/ ) {  
      ($hour,$min,$sec)  = ($1,$2,$3);
    }  
    $time = &ParseDate( $date . " " . $heure );
    if (! $time) {
      $julien = 1e+36; 
    } 
    else {
      # transforme le day_of_year en julian day
      $julien = &UnixDate($time,"%j") -1;
      $julien=&julian( $julien,
                       &UnixDate($time,"%H"),&UnixDate($time,"%M"),
		       &UnixDate($time,"%S") );
      $year = &UnixDate($time,"%Y");		  
    }
    # if position is decimal (4,8514003	-14,1495114), comment the
    # following lines, 
    # replace $lat_dec,$long_dec in split by $lat,$long
    # signe ° => \xB0
    #
    if( $lat =~ /(\w)\s*(\d+)\xB0\s*(\d+)'\s*(\d+[,.]?\d+)''/ ) {
      ($lat_s,$lat_deg,$lat_min,$lat_sec) = ($1,$2,$3,$4);
       $lat_sec =~ s/\,/\./mg; 
       $lat_dec  = &position($lat_deg,$lat_min,$lat_sec,$lat_s);
    } else {
       $lat =~ s/\,/\./mg; 
       $lat_dec = $lat;
    }
    if( $long =~ /(\w)\s*(\d+)\xB0\s*(\d+)'\s*(\d+[,.]?\d+)''/ ) {
      ($long_s,$long_deg,$long_min,$long_sec) = ($1,$2,$3,$4);
       $long_sec =~ s/\,/\./mg; 
       $long_dec = &position($long_deg,$long_min,$long_sec,$long_s);
    } else {
       $long =~ s/\,/\./mg; 
       $long_dec = $long;
    }
    # end comment for decimal position
    #
    ($lat_deg,$lat_min,$lat_s) = &positionSexa($lat_dec,'lat');
    ($long_deg,$long_min,$long_s) = &positionSexa($long_dec,'long');

    printf SSTD_FILE "%4d %10.9g %+08.4f %+09.4f %6.5g %6.5g %6.5g %6.5g\n",
       $year,$julien,$lat_dec,$long_dec,$SSJT,$SSPS,$CNDC,$SSTP;
    printf SNDD_FILE "%4d %10.9g %+08.4f %+09.4f %6.5g  %6.5g %6.5g %6.5g    %6.5g       %6.5g      %6.5g     %6.5g     %6.5g\n",
       $year,$julien,$lat_dec,$long_dec,$sonde,$sog,$cog,$speed,$heading,$speed_drift,$heading_drift,$phinsb,$phinst;
    printf MTOD_FILE "%4d %10.9g %+08.4f %+09.4f %5.4g %5.4g %5.4g %5.4g %5.4g %5.4g %5.4g\n",
      $year,$julien,$lat_dec,$long_dec,$tmer,$tair,$vit,$dir,$patm,$hum,$rad;
    printf FBOXD_FILE "%4d %10.9g %+08.4f %+09.4f  %6.5g %6.5g %6.5g   %6.5g    %6.5g    %6.5g     %6.5g     %6.5g %6.5g %6.5g\n",
       $year,$julien,$lat_dec,$long_dec,$DOX2,$SSPS_45,$TUR4,$Greenalgea,$BlueAlgae,$Diatoms,$Cryptophyta,$YellowSub,$CPHL,$PHPH;
    printf SST_FILE "%s %s  %02d°%06.3f %s  %03d°%06.3f %s  %6.5g %6.5g %6.5g %6.5g\n", 
      $date,$heure,$lat_deg,$lat_min,$lat_s,$long_deg,$long_min,$long_s,$SSJT,$SSPS,$CNDC,$SSTP;
    printf SND_FILE "%s %s  %02d°%06.3f %s  %03d°%06.3f %s %6.5g  %6.5g %6.5g %6.5g   %6.5g  %6.5g      %6.5g    %6.5g   %6.5g\n", 
      $date,$heure,$lat_deg,$lat_min,$lat_s,
      $long_deg,$long_min,$long_s,$sonde,$sog,$cog,$speed,$heading,$speed_drift,$heading_drift,$phinsb,$phinst;
    printf MTO_FILE "%s %s  %02d°%06.3f %s  %03d°%06.3f %s  ".
                    "%5.4g %5.4g %5.4g %5.4g %5.4g %5.4g %5.4g\n", 
       $date,$heure,$lat_deg,$lat_min,$lat_s,
       $long_deg,$long_min,$long_s,$tmer,$tair,$vit,$dir,$patm,$hum,$rad;
    printf FBOX_FILE "%s %s  %02d°%06.3f %s  %03d°%06.3f %s   %6.5g %6.5g %6.5g   %6.5g    %6.5g    %6.5g     %6.5g     %6.5g %6.5g %6.5g\n", 
      $date,$heure,$lat_deg,$lat_min,$lat_s,$long_deg,$long_min,$long_s,$DOX2,$SSPS_45,$TUR4,$Greenalgea,$BlueAlgae,$Diatoms,$Cryptophyta,$YellowSub,$CPHL,$PHPH;
    printf $TSGQC_HDL  
          "%04d %02d %02d %02d %02d %02d   %+10.7f   %+11.7f  %6.5g 0    NaN    NaN 0 %6.5g 0    NaN    NaN 0  %6.5g 0   NaN   NaN 0\n", 
          $year,$month,$day,$hour,$min,$sec,$lat_dec,$long_dec,
          $SSPS,$SSJT,$SSTP;   
    if( $tmer != 1e36 and $SSTP != 1e36) {		     
      $jmet = $jmet + 1;
      $dif_met = $tmer - $SSTP + $dif_met;
    }
    if( $SSJT != 1e36 and $SSTP != 1e36) {		     
      $jsbe = $jsbe + 1;
      $dif_sbe = $SSJT - $SSTP + $dif_sbe;
    }
  }
  $. = 0;
}  
$ecart = $dif_met / $jmet;
printf STDERR "Ecart moy Tmer  - SSTP  : %5.3f sur $jmet mesures\n", $ecart;
$ecart = $dif_sbe / $jsbe;
printf STDERR "Ecart moy SSJT - SSTP  : %5.3f sur $jsbe mesures\n", $ecart;

close SSTD_FILE;
close SST_FILE;
close SNDD_FILE;
close SND_FILE;
close MTOD_FILE;
close MTO_FILE;
close FBOXD_FILE;
close FBOX_FILE;

__DATA__
