#!/usr/bin/perl -w
#
# sta-fr22.pl
#
#  Genere un fichier des stations pour cascade a partir des fichiers
#  Seabird .btl
#
# $Id J Grelet may 2011$
#
use strict; # necessite de declarer toutes les variables globales
#use diagnostics;

use Time::Local;
use Date::Manip;
use File::Basename;
use Data::Dumper;

#------------------------------------------------------------------------------
# Les variables globales
#------------------------------------------------------------------------------
# fichier de sortie ASCII:
my  $sta_file = "FR22_sta.list";

# fichiers bouteille seabird .btl
my  $sbe_file;

my $ECHO = undef;

my ($s_date, $e_date, $date, $mois, $jour, $annee, $heure, $min, $time, $e_time);
my  $station;

#------------------------------------------------------------------------------
# usage()
#------------------------------------------------------------------------------	
sub usage() {
  print STDERR "\nusage: sta-fr22.pl [options] <files>\n\n";
  print STDERR   "examples:\n\$ perl sta-fr22.pl ../../CTD/data/FR22*.btl
  ../../CTD/data/fr22*.btl\n"; 
  exit 1;
}
#------------------------------------------------------------------------------
# Debut du programme principal
#------------------------------------------------------------------------------
&Date_Init( "TZ=UTC" );
&usage if( $#ARGV == -1);

# ouvre les fichiers de sortie
open( STA_FILE, "+> $sta_file" ) or die "Can't open file : $sta_file\n";

# parcourt des fichiers .btl passes en argument sur la ligne de commande
for( my $i = 0; $i <= $#ARGV; $i++ ){
  my $fileName = $ARGV[$i];

  # ouverture du fichier
  open( DATA_FILE, $fileName );
  print STDERR  "\nLit: $fileName  = " if defined $ECHO;

  # recupere le numero de la station dans le nom du fichier
  ($station) = ($fileName =~ m/FR22(\d{3})/i);

  # on lit le fichier bouteille
  while( <DATA_FILE> ){  
    # decode la date et heure de debut de station	  
    if( /System UpLoad Time =\s+(\.*)/)	{ # a modifier suivant le contexte
      ($time)  = /System UpLoad Time =\s+(\w+\s+\d+\s+\d+\s+\d+:\d+:\d+)/;	
      $date=&ParseDate($time);
      $s_date = &UnixDate($date,"%d/%m/%Y %H:%M:%S");
     }
     # decode la date de chaque prelevement
     if( /^\s+\d+\s+\w+\s+\d+\s+\d+/) {
       ($time) = /\s+\d+\s+(\w+\s+\d+\s+\d+)/;	
       $date = &ParseDate($time);
       $e_date = &UnixDate($date,"%d/%m/%Y");	      
     }
     # decode l'heure sur la ligne suivante
     if( /\s+(\d+:\d+:\d+)/) {
       ($time) = /\s+(\d+:\d+:\d+)/;	
       $date = &ParseDate($time);
       $e_time = &UnixDate($date,"%H:%M:%S");	      
      }
  }
  # pour chaque fichier, on garde la date et heure de la derniere bouteille
  # impression a l'ecran
  printf STDERR "%d %s %s %s\n", $station, $s_date,$e_date,$e_time;

  # impression dans le fichier 
  printf STA_FILE "%d %s %s %s\n", $station, $s_date,$e_date,$e_time; 
}  

printf STDERR "\n";;
